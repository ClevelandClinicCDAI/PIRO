import json
import requests
from sqlalchemy import text
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_certificate_path_concentriq
from tasks.utils.concentriq_setup import (
    get_concentriq_case_details_import_url,
    get_concentriq_header_auth,
    get_concentriq_case_page_size,
)

logger = get_logger()


class ConcentriqCaseLoader:
    """Class for loading case data into SOLR. The source data table is CohortCase_Delta. SOLR import handler is triggered for the data load"""  # noqa: E501

    def __init__(self):
        logger.info("ConcentriqCaseLoader constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

        self._authentication_header = get_concentriq_header_auth()
        self.concentriq_loader_url = get_concentriq_case_details_import_url()
        self._certificates_path: str = get_certificate_path_concentriq()
        self._pageSize: int | None = get_concentriq_case_page_size()
        logger.info("ConcentriqCaseLoader constructor-Start")

    def should_we_process_concentriq_data(self) -> bool:

        select_query = text(
            """Select [VALUE] from [dbo].[ConcentriqConfig] WHERE [KEY] = 'CaseDetails.Get.Enabled' And IsActive = 1"""  # noqa: E501
        )  # noqa: E501
        isEnabled = self._piro_db_connection.execute(select_query).scalar()
        if isEnabled is None:
            logger.info(
                (
                    "CaseDetails.Get.Enabled not configured. "
                    "Please configure and enable in the dbo.ConcentriqConfig table."  # noqa: E501
                )
            )  # noqa: E501
        return False if isEnabled is None else True

    def close_db_connection(self) -> None:
        """Close any connections to the database."""

        self._piro_db_session.close()
        self._piro_db_connection.close()

    def associate_concentriq_records_with_cases(self):
        """Associates records in the ConcentriqCase table with records in the
        main Case table."""

        sql = text("""EXEC [dbo].[P_AIRFLOW_Concentriq_Case_Load]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        return True

    def delete_concentriq_case_data(self):
        """Deletes all Concentriq records in the PIRO database."""

        sql = text("""EXEC dbo.[P_AIRFLOW_Concentriq_Case_Delete]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        return True

    def _get_case_key_max(self) -> int:
        try:
            select_query = text("""
                select Max(ConcentriqCaseId) ConcentriqCase
                from dbo.ConcentriqCase
                """)
            data = self._piro_db_connection.execute(select_query).scalar()

            if data is None:
                data = 0

            return data
        except Exception as e:
            logger.error(f"Error processing _get_case_key_max: {e}")
            return 0

    def get_concentriq_data(self) -> bool:
        """Retrieves data from Concentriq and adds it to the ConcentriqCase
        table in the PIRO database."""

        key = self._get_case_key_max()
        if key is None:
            return False
        process_data: bool = True

        while process_data:
            # key = 10
            logger.info(f"key: {key}")
            data = {
                "eager": {"$where": {"id": {"$gt": key}}},
                "limit": self._pageSize,
                "offset": 0,
                "fields": ["id", "accessionDate", "accessionId"],
                "order": [{"column": "id", "order": "asc"}],
            }
            json_string = json.dumps(data)
            logger.info(f"json_string: {json_string}")
            concentriq_url = (
                f"{self.concentriq_loader_url}?filter={json_string}"
            )
            if data is None:
                return True

            headers = {
                "Authorization": f"Basic {self._authentication_header}",
                "Content-Type": "application/json",
            }
            load_url = f"{concentriq_url}"
            logger.info(f"load_url: {load_url}")
            response = requests.get(
                load_url,
                headers=headers,
                verify=self._certificates_path,  # noqa: E501
            )
            logger.info(f"response.status_code: {response.status_code}")
            if response.status_code != 200:
                logger.error(
                    f"Error processing a batch: {response.status_code}"
                    f"{response.text}"
                )
                raise Exception(
                    f"Error in API data load call: {response.status_code}, Reason: {response.reason}, Decrease the batch size and try"  # noqa: E501
                )
            else:
                response_json = response.json()
                logger.info(f"response_json: {response_json}")
                response_items_json = response_json["items"]
                logger.info(f"response_items_json: {response_items_json}")
                if len(response_items_json) == 0:
                    logger.info("No more data to process")
                    process_data = False
                else:
                    response_items_str = json.dumps(response_items_json)
                    sql = text(
                        "EXEC [dbo].[P_AIRFLOW_Concentriq_Case_Insert] :items"  # noqa: E501
                    )
                    self._piro_db_session.execute(  # noqa: E501
                        sql, {"items": response_items_str}
                    )
                    self._piro_db_session.commit()
                    key = response_items_json[-1]["id"]

        return True
