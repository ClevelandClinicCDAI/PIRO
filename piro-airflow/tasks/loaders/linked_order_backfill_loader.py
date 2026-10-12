"""This class was created to correct issues with 'Linked Order' data in PIRO.
Specifically, historical linked order records were being erroneously purged
from the database.  This class will be used to backfill the missing linked
order records from Clarity.  Once all historical records have been added to
PIRO, this code can be retired.

Note that, when executing this on localhost on Windows, the script will error
because it will try to use the `set_var` function to update the Airflow
Variables table, which is not available on localhost.  This is not an issue on
the servers, so can be ignored.
"""

import oracledb

from collections.abc import Generator
from datetime import date, datetime
from typing import cast
from sqlalchemy import text
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from tasks.utils.database_setup import (
    get_clarity_db_connection,
    get_piro_db_engine,
    get_piro_db_session,
)
from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var, set_var

logger = get_logger()


class LinkedOrderBackfillLoader:
    """This class is responsible for backfilling missing linked order records
    from Clarity into the PIRO database."""

    def __init__(self):
        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )
        self._clarity_db_connection: oracledb.Connection = (
            get_clarity_db_connection(test_connection=True)
        )
        self._start_date: str = get_var("LINKED_ORDER_BACKFILL_START_DATE")
        self._end_date: str = get_var("LINKED_ORDER_BACKFILL_END_DATE")

    def load(self, max_requisition_ids_to_process: int | None = None) -> None:
        """Backfill missing linked order records from Clarity into the PIRO
        database.

        Records are grouped into per-requisition ID batches in order to ensure
        that all are processed as a group."""

        column_names: tuple[str, ...]
        row_iter: Generator[tuple, None, None]
        column_names, row_iter = self._get_clarity_linked_order_records()
        logger.info(
            "Clarity query executed for date window %s to %s."
            " Beginning to stream records.",
            self._start_date,
            self._end_date,
        )

        counter: int = 0
        row_count: int = 0
        current_requisition_id: int | None = None
        current_group: list[dict] = []
        stopped_early: bool = False

        for row in row_iter:
            row_count += 1
            record = dict(zip(column_names, row))
            requisition_id = record["REQUISITION_ID"]

            if current_requisition_id is None:
                current_requisition_id = requisition_id

            if requisition_id != current_requisition_id:
                self._process_linked_order_records(records=current_group)
                counter += 1
                if (
                    max_requisition_ids_to_process
                    and counter >= max_requisition_ids_to_process
                ):
                    stopped_early = True
                    row_iter.close()
                    break

                current_requisition_id = requisition_id
                current_group = [record]
                continue

            current_group.append(record)

        # If we stopped early, we want to process the last group of records
        if (
            not stopped_early
            and current_group
            and (
                max_requisition_ids_to_process is None
                or counter < max_requisition_ids_to_process
            )
        ):
            self._process_linked_order_records(records=current_group)
            counter += 1

        if not stopped_early:
            logger.info(
                "Streaming complete. %s row(s) retrieved across"
                " %s requisition ID group(s).",
                row_count,
                counter,
            )
            self._shift_date_window_back()

    def _get_clarity_linked_order_records(
        self,
    ) -> tuple[tuple[str, ...], Generator[tuple, None, None]]:
        """Get linked order records from Clarity that fall within the defined
        start and end dates.

        Note that the start_date in this query is 'inclusive' and the end_date
        is 'exclusive'.  All records from midnight of the start_date through
        11:59:59 PM of the day before the end_date will be retrieved.
        """

        query: str = """
            SELECT
                specimen_tests.LAST_RECV_UTC_DTTM,
                order_results.RESULT_DATE,
                order_procedures.UPDATE_DATE,
                order_procedures.ORDER_INST,
                order_procedures.REVIEW_TIME,
                requisition_specimens.REQUISITION_ID,
                lab_case_info.CASE_NUM,
                specimen_tests.SPEC_TST_ORDER_ID,
                order_links.ORDER_ID,
                order_results.ORDER_PROC_ID,
                clarity_component.COMPONENT_ID,
                clarity_component.NAME                       COMP_NAME,
                clarity_component.EXTERNAL_NAME              COMP_EXTERNAL_NAME,
                clarity_component.DFLT_UNITS,
                order_procedures.PROC_ID,
                order_procedures.DESCRIPTION                 PROC_DESC,
                specimen_tests.SPEC_NUMBER_RLTD,
                requisition_specimens.LINE                   SPEC_LINE,
                specimen_tests.LINE                          SPEC_TEST_LINE,
                order_links.LINE                             LINKED_ORD_LINE,
                order_results.ORD_VALUE,
                order_results.ORD_NUM_VALUE,
                order_results.REFERENCE_LOW,
                order_results.REFERENCE_HIGH,
                order_results.REFERENCE_UNIT,
                order_results.ORD_RAW_VALUE,
                order_results.RAW_LOW,
                order_results.RAW_HIGH,
                specimen_tests.REPORTABLE_YN
                FROM LAB_CASE_INFO lab_case_info
            JOIN REQ_SPECIMEN requisition_specimens ON requisition_specimens.REQUISITION_ID = lab_case_info.REQUISITION_ID
            JOIN SPEC_TEST_REL specimen_tests ON specimen_tests.SPECIMEN_ID = requisition_specimens.REQ_SPECIMEN_ID
            JOIN ORD_LAB_LINKED_ORD order_links ON order_links.ORDER_ID = specimen_tests.SPEC_TST_ORDER_ID
            JOIN CLARITY.ORDER_RESULTS order_results ON order_results.ORDER_PROC_ID = order_links.LAB_LINKED_ORD_ID
            JOIN CLARITY.CLARITY_COMPONENT clarity_component ON clarity_component.COMPONENT_ID = order_results.COMPONENT_ID
            JOIN CLARITY.ORDER_PROC order_procedures ON order_procedures.ORDER_PROC_ID = order_results.ORDER_PROC_ID
            WHERE requisition_specimens.LINE = 1
            AND (
                (order_results.RESULT_DATE >= TO_DATE(:start_date, 'yyyy-mm-dd') AND order_results.RESULT_DATE < TO_DATE(:end_date, 'yyyy-mm-dd'))
                OR
                (order_procedures.REVIEW_TIME >= TO_DATE(:start_date, 'yyyy-mm-dd') AND order_procedures.REVIEW_TIME < TO_DATE(:end_date, 'yyyy-mm-dd'))
            )
            ORDER BY requisition_specimens.REQUISITION_ID
        """  # noqa:E501
        cursor = self._clarity_db_connection.cursor()
        cursor.execute(
            query,
            {"start_date": self._start_date, "end_date": self._end_date},
        )
        cursor_description = cursor.description or []
        column_names = tuple(
            cast(str, description[0]) for description in cursor_description
        )

        def _row_generator() -> Generator[tuple, None, None]:
            """Yield rows in batches and ensure the cursor is closed."""

            try:
                while True:
                    rows = cursor.fetchmany(1000)
                    if not rows:
                        break
                    for row in rows:
                        yield row
            finally:
                cursor.close()

        return column_names, _row_generator()

    def _process_linked_order_records(self, records: list[dict]) -> None:
        """Process linked order records for a given requisition ID."""

        requisition_id: int = records[0]["REQUISITION_ID"]

        if self._requisition_id_already_exists(requisition_id):
            logger.info(
                f"Requisition ID {requisition_id} already exists in the LinkedOrder table. Skipping processing."  # noqa:E501
            )
            return
        else:
            case_id: int | None = self._get_case_id_for_requisition_id(
                requisition_id
            )
            if not case_id:
                logger.error(
                    f"Case ID not found for Requisition ID {requisition_id}. Skipping processing."  # noqa:E501
                )
                return
            self._insert_linked_order_records(records, case_id)

    def _requisition_id_already_exists(self, requisition_id: int) -> bool:
        """Check if a given requisition ID already exists in the LinkedOrder
        table."""

        query = text("""
            SELECT CASE WHEN EXISTS (
                SELECT 1
                  FROM LinkedOrder
                 WHERE RefRequisitionId = :requisition_id
            ) THEN 'Yes' ELSE 'No' END AS value_exists;
            """)

        result: str = self._piro_db_session.scalar(
            query, {"requisition_id": requisition_id}
        )
        return result == "Yes"

    def _get_case_id_for_requisition_id(
        self, requisition_id: int
    ) -> int | None:
        """Get the CaseId for a given RequisitionId from the Case table."""

        query = text("""
            SELECT CaseId
              FROM [Case]
             WHERE RefRequisitionId = :requisition_id
            ;
            """)

        result: int | None = self._piro_db_session.scalar(
            query, {"requisition_id": requisition_id}
        )
        return result

    def _insert_linked_order_records(
        self, records: list[dict], case_id: int
    ) -> None:
        """Insert linked order records into the LinkedOrder table."""

        formatted_records: list[dict] = self._format_linked_order_records(
            source_records=records, case_id=case_id
        )

        if not formatted_records:
            logger.info("No linked order records to insert.")
            return

        insert_query = text("""
            INSERT INTO LinkedOrder (
                CaseId,
                ComponentName,
                ComponentExternalName,
                ProcedureDesc,
                DefaultUnit,
                OrdValue,
                OrdNumValue,
                OrdLow,
                OrdHigh,
                OrdUnit,
                OrdRawValue,
                OrdRawHigh,
                OrdRawLow,
                ResultDate,
                OrderDate,
                ReviewDate,
                RefRequisitionId,
                RefSpecTestOrderId,
                RefOrderId,
                RefOrderProcId,
                RefComponentId,
                RefProcId,
                CreateDate,
                CreateBy,
                UpdateDate,
                UpdateBy
            )
            VALUES (
                :CaseId,
                :ComponentName,
                :ComponentExternalName,
                :ProcedureDesc,
                :DefaultUnit,
                :OrdValue,
                :OrdNumValue,
                :OrdLow,
                :OrdHigh,
                :OrdUnit,
                :OrdRawValue,
                :OrdRawHigh,
                :OrdRawLow,
                :ResultDate,
                :OrderDate,
                :ReviewDate,
                :RefRequisitionId,
                :RefSpecTestOrderId,
                :RefOrderId,
                :RefOrderProcId,
                :RefComponentId,
                :RefProcId,
                :CreateDate,
                :CreateBy,
                :UpdateDate,
                :UpdateBy
            )
            """)

        with self._piro_db_engine.begin() as connection:
            connection.execute(insert_query, formatted_records)

        logger.info(
            "Inserted %s linked order records for requisition ID %s.",
            len(formatted_records),
            formatted_records[0]["RefRequisitionId"],
        )

    def _format_linked_order_records(
        self, source_records: list[dict], case_id: int
    ) -> list[dict]:
        """Format the source data into a format that can be inserted into the
        database."""

        formatted_records: list = []
        for source_record in source_records:
            formatted_record: dict = {}
            formatted_record["CaseId"] = case_id
            formatted_record["ComponentName"] = source_record["COMP_NAME"]
            formatted_record["ComponentExternalName"] = source_record[
                "COMP_EXTERNAL_NAME"
            ]
            formatted_record["ProcedureDesc"] = source_record["PROC_DESC"]
            formatted_record["DefaultUnit"] = source_record["DFLT_UNITS"]
            formatted_record["OrdValue"] = source_record["ORD_VALUE"]
            formatted_record["OrdNumValue"] = source_record["ORD_NUM_VALUE"]
            formatted_record["OrdLow"] = source_record["REFERENCE_LOW"]
            formatted_record["OrdHigh"] = source_record["REFERENCE_HIGH"]
            formatted_record["OrdUnit"] = source_record["REFERENCE_UNIT"]
            formatted_record["OrdRawValue"] = source_record["ORD_RAW_VALUE"]
            formatted_record["OrdRawHigh"] = source_record["RAW_LOW"]
            formatted_record["OrdRawLow"] = source_record["RAW_HIGH"]
            formatted_record["ResultDate"] = source_record["RESULT_DATE"]
            formatted_record["OrderDate"] = source_record["ORDER_INST"]
            formatted_record["ReviewDate"] = source_record["REVIEW_TIME"]
            formatted_record["RefRequisitionId"] = source_record[
                "REQUISITION_ID"
            ]
            formatted_record["RefSpecTestOrderId"] = source_record[
                "SPEC_TST_ORDER_ID"
            ]
            formatted_record["RefOrderId"] = source_record["ORDER_ID"]
            formatted_record["RefOrderProcId"] = source_record["ORDER_PROC_ID"]
            formatted_record["RefComponentId"] = source_record["COMPONENT_ID"]
            formatted_record["RefProcId"] = source_record["PROC_ID"]
            formatted_record["CreateDate"] = datetime.now()
            formatted_record["CreateBy"] = "airflow_backfill_script"
            formatted_record["UpdateDate"] = None
            formatted_record["UpdateBy"] = None
            formatted_records.append(formatted_record)

        return formatted_records

    def _shift_date_window_back(self) -> None:
        """Shift the start and end date window backwards by the same duration
        as the current window, so the next run processes the preceding
        timespan.

        Example: if start = 2026-01-15 and end = 2026-01-16 (delta = 1 day),
        then new start = 2026-01-14 and new end = 2026-01-15.
        """

        start: date = date.fromisoformat(self._start_date)
        end: date = date.fromisoformat(self._end_date)
        delta = end - start

        new_start: date = start - delta
        new_end: date = start

        set_var("LINKED_ORDER_BACKFILL_START_DATE", new_start.isoformat())
        set_var("LINKED_ORDER_BACKFILL_END_DATE", new_end.isoformat())

        logger.info(
            "Date window shifted: start %s -> %s, end %s -> %s.",
            self._start_date,
            new_start.isoformat(),
            self._end_date,
            new_end.isoformat(),
        )

        self._start_date = new_start.isoformat()
        self._end_date = new_end.isoformat()

    def close_db_connections(self) -> None:
        """Close the database connections."""

        self._clarity_db_connection.close()
        self._piro_db_session.close()
        self._piro_db_engine.dispose()
