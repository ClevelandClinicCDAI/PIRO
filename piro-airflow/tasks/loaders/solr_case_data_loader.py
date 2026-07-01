import json
import datetime
import requests
from sqlalchemy import text
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_certificate_path_solr
from tasks.utils.solr_setup import (
    get_solr_case_data_import_url,
    get_solr_case_data_update_url,
    get_solr_case_update_batch_size,
)
from tasks.utils.solr_setup import get_solr_case_status_url
from tasks.utils.solr_setup import get_solr_header_auth
from tasks.utils.solr_setup import get_solr_case_data_count_url
import time

logger = get_logger()


class SolrCaseDataLoader:
    """Class for loading case data into SOLR. The source data table is CohortCase_Delta. SOLR import handler is triggered for the data load"""  # noqa: E501

    def __init__(self):
        logger.info("SolrCaseDataLoader constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

        self._authentication_header = get_solr_header_auth()
        self.solr_loader_url = get_solr_case_data_import_url()
        self.solr_update_url = get_solr_case_data_update_url()
        self.solr_status_url = get_solr_case_status_url()
        self.solr_data_count_url = get_solr_case_data_count_url()
        self._certificates_path: str = get_certificate_path_solr()
        self.batch_size = get_solr_case_update_batch_size()

        logger.info("SolrCaseDataLoader constructor-Start")

    def _load_data(self) -> bool:
        """Function to call the solr data loader."""
        logger.info("_load_data-Start")

        sql_delta_count = self.get_sql_record_delta_count()
        sql_full_count = self.get_sql_record_full_count()
        solr_pre_count = self.get_solr_record_count()

        logger.info(f"solr_pre_count: {solr_pre_count}")
        logger.info(f"sql_delta_count: {sql_delta_count}")
        logger.info(f"sql_full_count: {sql_full_count}")

        logger.info("solr_loader_url-Start")
        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        timestamp_int = int(datetime.datetime.utcnow().timestamp())
        load_url = f"{self.solr_loader_url}&_={timestamp_int}"
        load_response = requests.get(
            load_url,
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

            # if data_load["status"] == "idle":
            #     raise Exception(
            #         "SOLR data load not triggered. The response returned is idle instead of busy."  # noqa: E501
            #     )  # noqa: E501

            logger.info("solr_status_url-Start")
            logger.info(self.solr_status_url)
            while True:
                time.sleep(5)
                status_response = self._load_data_status()
                data_status = status_response.json()
                logger.info(f"data_status: {data_status['status']}")
                if data_status["status"] == "idle":
                    break
            logger.info("solr_status_url-End")

        solr_post_count = self.get_solr_record_count()

        logger.info(f"solr_pre_count: {solr_pre_count}")
        logger.info(f"sql_delta_count: {sql_delta_count}")
        logger.info(f"sql_full_count: {sql_full_count}")
        logger.info(f"solr_post_count: {solr_post_count}")

        if sql_full_count != solr_post_count:
            raise Exception(
                f"SQL and SOLR data counts did not match. SQL count: {sql_full_count}, SOLR count: {solr_post_count}"  # noqa: E501
            )  # noqa: E501

        logger.info("_load_data-End")
        return True

    def are_there_records_to_load(self) -> bool:
        """Query the V_AIRFLOW_Case_Data_Load view for records to be loaded in SOLR."""  # noqa: E501
        select_query = text(
            """SELECT count(0) From [dbo].[V_AIRFLOW_Case_Data_Load]"""
        )  # noqa: E501
        recordCount = self._piro_db_connection.execute(select_query).scalar()
        return True if recordCount > 0 else False

    def get_sql_record_delta_count(self) -> int:
        """Query the V_AIRFLOW_Case_Data_Load view for records to be loaded in SOLR."""  # noqa: E501
        select_query = text(
            """SELECT count(0) From [dbo].[V_AIRFLOW_Case_Data_Load]"""
        )  # noqa: E501
        recordCount = self._piro_db_connection.execute(select_query).scalar()
        return recordCount

    def get_sql_record_full_count(self) -> int:
        """Query the CaseSolr view for records to be loaded in SOLR."""  # noqa: E501
        select_query = text(
            """SELECT count(0) From [dbo].[CaseSolr]"""
        )  # noqa: E501
        recordCount = self._piro_db_connection.execute(select_query).scalar()
        return recordCount

    def get_solr_record_count(self) -> int:
        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        data_count_url = f"{self.solr_data_count_url}"
        data_count_response = requests.get(
            data_count_url,
            headers=headers,
            verify=self._certificates_path,  # noqa: E501
        )

        if data_count_response.status_code != 200:
            raise Exception(
                f"Error in API data count call: {data_count_response.status_code}"
            )  # noqa: E501
        else:
            data_count = data_count_response.json()
            logger.info(f"Load check: {data_count}")

            if data_count["response"]:
                return int(data_count["response"]["numFound"])
            else:
                return 0

    def _load_data_status(self) -> requests.Response:
        """Function to call the solr data loader."""

        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        # logger.info("solr_loader_url-start")
        # logger.info(self.solr_status_url)
        timestamp_int = int(datetime.datetime.utcnow().timestamp())
        url_time = f"{self.solr_status_url}&_={timestamp_int}"
        response = requests.get(
            url_time,
            headers=headers,
            verify=self._certificates_path,  # noqa: E501
        )
        # logger.info("solr_loader_url-End")
        if response.status_code != 200:
            raise Exception(
                f"Error in API status call: {response.status_code}"
            )  # noqa: E501

        return response

    def reset_data_for_next_load(self):
        sql = text("""EXEC dbo.[P_AIRFLOW_Case_Solr_Delete]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        return True

    def close_db_connection(self) -> None:
        """Close any connections to the database."""
        self._piro_db_session.close()
        self._piro_db_connection.close()

    def delete_solr_staging_data(self):
        sql = text("""EXEC dbo.[P_AIRFLOW_Case_Solr_Delete]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()

        sql = text("""Truncate Table dbo.[CaseSolr_Preload]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()

        return True

    def _get_case_data(self, start_key: int, data_record_count: int) -> list:
        select_query = text(f"""
            declare @queue nvarchar(max)
            select @queue = (
                Select TOP {int(float(data_record_count))} *
            from dbo.V_AIRFLOW_Solr_Case
            WHERE [caseid] > {start_key}
            Order by [caseid]
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

    def _get_case_data_key_min(self) -> int:
        select_query = text(f"""
            SELECT Min([id]) Min_id, Max([id]) Max_id
            FROM dbo.V_AIRFLOW_Solr_Case
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
        """Uploads Case records to Solr."""

        key = self._get_case_data_key_min()
        if key is None:
            return False

        data_record_count: int = self.batch_size
        process_data: bool = True
        retry_index: int = 0
        while process_data:
            logger.info(f"key: {key}")
            data = self._get_case_data(key, data_record_count)
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
                verify=self._certificates_path,
                data=json.dumps(data),
            )
            logger.info(f"response: {response.status_code}")

            if response.status_code != 200:
                logger.error(
                    f"Error processing a batch: {response.status_code} {response.text}"  # noqa:E501
                )
                # on error, decrease the batch size by 10 and retry
                data_record_count: int = round(self.batch_size / 10)
                retry_index = retry_index + 1
                if retry_index > 3:
                    raise Exception(
                        f"Error in API data load call: {response.status_code}, Reason: {response.reason}, Decrease the batch size and try"  # noqa: E501
                    )
            else:
                key = data[-1]["id"]
                data_record_count: int = self.batch_size
                retry_index = 0
        return True
