import datetime
import json
import requests
from sqlalchemy import text
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_certificate_path_solr
from tasks.utils.solr_setup import (
    get_solr_case_staff_data_import_url,
    get_solr_case_staff_data_update_url,
    get_solr_case_staff_data_update_batch,
)
from tasks.utils.solr_setup import get_solr_case_staff_status_url
from tasks.utils.solr_setup import get_solr_header_auth
import time

logger = get_logger()


class SolrCaseStaffLoader:
    """Class for loading case data into SOLR. The source data table is CohortCase_Delta. SOLR import handler is triggered for the data load"""  # noqa: E501

    def __init__(self):
        logger.info("SolrCaseStaffLoader constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

        self._authentication_header = get_solr_header_auth()
        self.solr_loader_url = get_solr_case_staff_data_import_url()
        self.solr_update_url = get_solr_case_staff_data_update_url()
        self.solr_status_url = get_solr_case_staff_status_url()
        self.solr_update_batch = get_solr_case_staff_data_update_batch()
        self._certificates_path: str = get_certificate_path_solr()

        logger.info("SolrCaseStaffLoader constructor-Start")

    def _load_data(self) -> bool:
        """Function to call the solr data loader."""
        logger.info("_load_data-Start")

        logger.info("solr_loader_url-Start")
        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
        }
        # load_data = {
        #     "command": "full-import",
        #     "verbose": "false",
        #     "clean": "false",
        #     "commit": "true",
        #     "name": "dataimport",
        # }

        logger.info(self.solr_loader_url)
        # load_response = requests.post(
        #     self.solr_loader_url,
        #     data=json.dumps(load_data),
        #     headers=headers,
        #     verify=self._certificates_path,
        # )

        load_response = requests.get(
            self.solr_loader_url,
            headers=headers,
            verify=self._certificates_path,  # noqa: E501
        )
        logger.info("solr_loader_url-End")
        if load_response.status_code != 200:
            raise Exception(
                f"Error in API data load call: {load_response.status_code}"
            )  # noqa: E501
        else:
            data_load = load_response.json()
            logger.info(f"Load check: {data_load}")
            logger.info("solr_status_url-Start")
            logger.info(self.solr_status_url)
            while True:
                status_response = self._load_data_status()
                data_status = status_response.json()
                logger.info(f"data_status: {data_status['status']}")
                if data_status["status"] == "idle":
                    break
                time.sleep(3)
            logger.info("solr_status_url-End")
        logger.info("_load_data-End")
        return True

    def are_there_records_to_load(self) -> bool:
        """Query the V_AIRFLOW_Case_Staff_Load view to determine if there are
        records that need to be loaded in SOLR."""

        select_query = text(
            """SELECT count(0) From [dbo].[V_AIRFLOW_Case_Staff_Load]"""  # noqa: E501
        )  # noqa: E501
        recordCount = self._piro_db_connection.execute(select_query).scalar()
        return True if recordCount > 0 else False

    def _load_data_status(self) -> requests.Response:
        """Function to call the solr data loader."""

        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            self.solr_status_url,
            headers=headers,
            verify=self._certificates_path,  # noqa: E501
        )

        if response.status_code != 200:
            raise Exception(
                f"Error in API status call: {response.status_code}"
            )

        return response

    def reset_data_for_next_load(self):
        sql = text("""EXEC dbo.[P_AIRFLOW_Case_Staff_Solr_Delete]""")

        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        return True

    def close_db_connection(self) -> None:
        """Close any connections to the database."""
        self._piro_db_session.close()
        self._piro_db_connection.close()

    def delete_staff_suggest_staging_data(self):
        sql = text("""EXEC dbo.[P_AIRFLOW_Case_Staff_Solr_Delete]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()

        return True

    def _get_case_staff_data(
        self, start_key: int, data_record_count: int
    ) -> list:
        # data_record_count: int = 10
        select_query = text(f"""
            declare @queue nvarchar(max)
            select @queue = (
                Select TOP {int(float(data_record_count))} [key], id, staffname
            from V_AIRFLOW_Solr_CaseStaff_Suggest
            WHERE [key] > {start_key}
            Order by [key]
            FOR JSON PATH)
            select @queue as JSON
            """)
        data = self._piro_db_connection.execute(select_query).scalar()
        if data is None:
            return None
        try:
            dataJson = json.loads(data)
            return dataJson if len(dataJson) > 0 else None
        except Exception as e:
            logger.error(f"Error processing a batch: {e}")
            return None

    def _get_case_staff_data_key_min(self) -> int:
        select_query = text(f"""
            SELECT Min([key]) Min_id, Max([key]) Max_id
            FROM dbo.V_AIRFLOW_Solr_CaseStaff_Suggest
            FOR JSON PATH
            """)
        data = self._piro_db_connection.execute(select_query).scalar()
        try:
            dataJson = json.loads(data)
            if len(dataJson) > 0:
                return dataJson[0]["Min_id"]
        except json.JSONDecodeError:
            return None

    def upload_records_to_solr(self) -> bool:
        """Function to call the solr data loader."""
        key = self._get_case_staff_data_key_min()
        if key is None:
            return False

        data_record_count: int = self.solr_update_batch
        process_data: bool = True
        retry_index: int = 0
        while process_data:
            logger.info(f"key: {key}")
            data = self._get_case_staff_data(key, data_record_count)
            if data is None:
                return True
            logger.info(f"data: {len(data)}")
            headers = {
                "Authorization": f"Basic {self._authentication_header}",
                "Content-Type": "application/json",
            }
            timestamp_int = int(datetime.datetime.utcnow().timestamp())
            load_url = f"{self.solr_update_url}&_={timestamp_int}"

            response = requests.post(
                load_url,
                headers=headers,
                verify=self._certificates_path,  # noqa: E501
                data=json.dumps(data),
            )
            # print(f"response: {response.status_code}")

            # if response.status_code != 200:
            #     raise Exception(
            #         f"Error in API status call: {response.status_code}"
            #     )

            # key = data[-1]["key"]
            if response.status_code != 200:
                logger.error(
                    f"Error processing a batch: {response.status_code} {response.text}"
                )
                data_record_count: int = self.solr_update_batch / 10
                retry_index = retry_index + 1
                if retry_index > 3:
                    raise Exception(
                        f"Error in API data load call: {response.status_code}, Reason: {response.reason}, Decrease the batch size and try"  # noqa: E501
                    )
            else:
                key = data[-1]["key"]
                data_record_count: int = self.solr_update_batch
                retry_index = 0
        return True
