import traceback
from typing import Generator
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import text
from airflow.sdk import Variable
from striprtf.striprtf import rtf_to_text
from tasks.utils.logging_setup import get_logger
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.models.main import CaseTextMasterPlain

logger = get_logger()


class RTFToPlainTextEpicCommentConverter:
    """RTF to Plain text comment converter.

    Retrieves RTF-formatted text from the CaseCommentEpic table in the PIRO database,
    converts it to plain text using the striprtf library, and saves the plain text to the
    CaseTextMasterPlain table so that it can, later, be used in LLM annotation tasks.
    """  # noqa: E501

    def __init__(
        self,
    ):
        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

    def convert(self, max_cases_to_process: int | None = None) -> dict:
        """Primary method.  Converts new - and updates existing - records."""

        max_cases_to_process = self._get_max_cases_to_process(
            max_cases_to_process
        )

        erroneous_comments_deleted: int = self._delete_erroneous_case_comments(
            max_cases_to_process
        )

        new_comments_converted: int = self._convert_comments_for_new_cases(
            max_cases_to_process
        )

        self._close_db_connection()

        return {
            "erroneous_comments_deleted": erroneous_comments_deleted,
            "new_records_converted": new_comments_converted,
        }

    def _get_max_cases_to_process(self, max_cases_to_process: int | None):
        """Determine how many records to process, using the specified value if
        available, or pulling from an Airflow Variable if not.

        Note that this value is used for conversion of new records AND for
        deletions of orphans and duplicates."""

        if max_cases_to_process:
            return max_cases_to_process
        else:
            return int(
                Variable.get("RTF_TO_PLAIN_TEXT_MAX_CASES", default=100000)
            )

    def _delete_erroneous_case_comments(
        self, max_cases_to_process: int
    ) -> int:
        """Delete all comments for any case where the comment count - by
        comment type - doesn't match the comments in the source table.

        We do this to capture any new comments added to a case after they have
        been converted, and to deal with duplicate issues from an early version
        of this task.
        """

        comment_ids_to_delete: list[int] = self._get_erroneous_comment_ids(
            max_cases_to_process
        )

        logger.info(
            f"Deleting {len(comment_ids_to_delete)} erroneous comment records (comment/commentType count mismatches)."  # noqa:E501
        )

        self._delete_plain_text_comments(plain_text_ids=comment_ids_to_delete)

        return len(comment_ids_to_delete)

    def _get_erroneous_comment_ids(
        self, max_cases_to_process: int
    ) -> list[int]:
        """Compare the number of comments by CaseID and CommentTypeID between
        the CaseCommentEpic and CaseTextMasterPlain tables, returning a list of
        all comments for cases where the comment counts don't match."""

        if not isinstance(max_cases_to_process, int):
            raise ValueError("Invalid value for 'max_cases_to_convert'.")

        erroneous_comments_query = text(f"""
            WITH converted_comment_counts AS (
                SELECT CaseId, CommentTypeId, COUNT(*) AS CommentTypeCount
                  FROM CaseTextMasterPlain
                 WHERE CaseCommentId IS NULL
                   AND CaseCommentCoPathId IS NULL
                   AND CaseCommentCoEpicId IS NOT NULL
                 GROUP BY CaseId, CommentTypeId
            ),
            epic_comment_counts AS (
                SELECT CaseId, CommentTypeId, COUNT(*) AS CommentTypeCount
                  FROM CaseCommentEpic
                 GROUP BY CaseId, CommentTypeId
            ),
            case_ids_with_invalid_comments AS (
                SELECT TOP {max_cases_to_process} converted_comment_counts.CaseID
                  FROM converted_comment_counts
                  LEFT OUTER JOIN epic_comment_counts
                    ON converted_comment_counts.CaseID = epic_comment_counts.CaseId
                   AND converted_comment_counts.CommentTypeId = epic_comment_counts.CommentTypeId
                   AND converted_comment_counts.CommentTypeCount = epic_comment_counts.CommentTypeCount
                 WHERE epic_comment_counts.CaseId IS NULL
                 GROUP BY converted_comment_counts.CaseID
                 ORDER BY converted_comment_counts.CaseID DESC
            )
            SELECT plain_text.PlainTextId
              FROM CaseTextMasterPlain plain_text
              JOIN case_ids_with_invalid_comments
                ON plain_text.CaseID = case_ids_with_invalid_comments.CaseID
            """)  # noqa:E501

        return (
            self._piro_db_connection.execute(erroneous_comments_query)
            .scalars()  # type: ignore
            .all()
        )

    def _delete_plain_text_comments(self, plain_text_ids: list[int]) -> None:
        """Delete the specified IDs from the CaseTextMasterPlain table."""

        id_batches: Generator = self._get_batches(
            items_to_batch=plain_text_ids
        )

        for id_batch in id_batches:
            delete_query = delete(CaseTextMasterPlain).where(
                CaseTextMasterPlain.PlainTextId.in_(id_batch)
            )
            self._piro_db_session.execute(delete_query)

            self._piro_db_session.commit()

    def _get_batches(
        self, items_to_batch: list, batch_size: int = 500
    ) -> Generator:
        """Split the list of source_records into batches."""

        for i in range(0, len(items_to_batch), batch_size):
            yield items_to_batch[i : i + batch_size]  # noqa

    def _convert_comments_for_new_cases(
        self, max_cases_to_process: int
    ) -> int:
        """Convert comments for any new cases."""

        records_to_convert: list = self._get_new_records_to_convert(
            max_cases_to_process
        )

        logger.info(f"Converting {len(records_to_convert)} comment records.")

        records: list[dict] = self._format_as_dicts(records_to_convert)

        self._convert_records(records)

        self._insert_into_plain_text_table(records)

        return len(records)

    def _get_new_records_to_convert(
        self, max_cases_to_process: int
    ) -> list[Row]:
        """Query the CaseCommentEpic table for new records to be converted.

        Specifically, we look for any cases that haven't yet been converted,
        rather than comments.  Because the comment IDs change over time, we
        cannot rely on comment IDs to know what has/hasn't been converted."""

        if not isinstance(max_cases_to_process, int):
            raise ValueError("Invalid value for 'max_cases_to_convert'.")

        new_comments_query = text(f"""
            WITH converted_epic_case_ids AS (
              SELECT CaseId
                FROM CaseTextMasterPlain
               WHERE CaseCommentCoEpicId IS NOT NULL
                 AND CaseCommentId IS NULL
                 AND CaseCommentCoPathId IS NULL
               GROUP BY CaseId
            ),
            unconverted_epic_case_ids AS (
                SELECT TOP {max_cases_to_process} epic_comments.CaseId
                  FROM CaseCommentEpic epic_comments
                  JOIN [Case] cases
                    ON epic_comments.CaseId = cases.CaseId
                  LEFT OUTER JOIN converted_epic_case_ids
                    ON cases.CaseId = converted_epic_case_ids.CaseID
                 WHERE converted_epic_case_ids.CaseID IS NULL
                 GROUP BY epic_comments.CaseId
            )
            SELECT epic_comments.CaseCommentCoEpicId,
                   epic_comments.CaseID,
                   cases.CaseNumber,
                   epic_comments.CommentTypeId,
                   epic_comments.RefLabCompName,
                   epic_comments.Text
              FROM CaseCommentEpic epic_comments
              JOIN [Case] cases
                ON epic_comments.CaseId = cases.CaseId
              JOIN unconverted_epic_case_ids
                ON epic_comments.CaseId = unconverted_epic_case_ids.CaseId
             ORDER BY cases.AccessionDate DESC
            """)

        return self._piro_db_connection.execute(
            new_comments_query
        ).fetchall()  # type: ignore

    def _format_as_dicts(self, records_to_convert: list[tuple]) -> list[dict]:
        """Format the records to be converted as dictionaries."""

        formatted_records: list = []

        for record in records_to_convert:
            try:
                record_dict = {
                    "CaseCommentCoEpicId": record[0],
                    "CaseId": record[1],
                    "CaseNumber": record[2],
                    "CommentTypeId": record[3],
                    "RefLabCompName": record[4],
                    "plain_Text": record[5],
                }

                formatted_records.append(record_dict)
            except Exception as e:
                logger.error(f"Error formatting a record as a dict: {e}")
                logger.error(traceback.format_exc())

        return formatted_records

    def _convert_records(self, records: list[dict]) -> None:
        """Convert the text of the comments from RTF into plain text."""

        converted_records: list[dict] = []

        for record in records:
            try:
                record["plain_Text"] = rtf_to_text(
                    record["plain_Text"], encoding="latin-1"
                )
                converted_records.append(record)
            except Exception as e:
                logger.error(
                    f"Error converting RTF to text: {e}. CaseCommentCoEpicId: {record['CaseCommentCoEpicId']}"  # noqa:E501
                )
                logger.error(traceback.format_exc())

        records[:] = converted_records

    def _insert_into_plain_text_table(self, records: list[dict]) -> None:
        """Insert the records into the plain text table.

        Utilizes SQLAlchemy's 'bulk_insert_mappings' method for performance."""

        self._piro_db_session.bulk_insert_mappings(
            CaseTextMasterPlain, records, render_nulls=True
        )

        self._piro_db_session.commit()

    def _close_db_connection(self) -> None:
        """Close any connections to the database."""

        self._piro_db_session.close()
        self._piro_db_connection.close()
