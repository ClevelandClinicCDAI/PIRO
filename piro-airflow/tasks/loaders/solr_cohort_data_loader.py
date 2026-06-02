import datetime
import json
import requests
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session
from sqlalchemy import text
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_certificate_path_solr
from tasks.utils.solr_setup import get_solr_cohort_data_update_url
from tasks.utils.solr_setup import get_solr_cohort_data_update_batch
from tasks.utils.solr_setup import get_solr_cohort_data_import_url
from tasks.utils.solr_setup import get_solr_cohort_status_url
from tasks.utils.solr_setup import get_solr_header_auth

import time

logger = get_logger()


class SolrCohortDataLoader:
    """Class for loading case data into SOLR. The source data table is CohortCase_Delta. SOLR import handler is triggered for the data load"""  # noqa: E501

    def __init__(self):
        logger.info("SolrCohortDataLoader constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

        self._authentication_header = get_solr_header_auth()
        self.solr_import_url = get_solr_cohort_data_import_url()
        self.solr_status_url = get_solr_cohort_status_url()
        self.solr_delete_url = get_solr_cohort_data_update_url()
        self.solr_update_url = get_solr_cohort_data_update_url()
        self.solr_update_batch = get_solr_cohort_data_update_batch()

        self._certificates_path: str = get_certificate_path_solr()
        logger.info(f"self._certificates_path: {self._certificates_path}")
        logger.info(f"self.solr_delete_url: {self.solr_delete_url}")
        logger.info(f"self.solr_import_url: {self.solr_import_url}")
        logger.info(f"self.solr_update_url: {self.solr_update_url}")
        logger.info(f"self.solr_update_batch: {self.solr_update_batch}")
        logger.info("SolrCohortDataLoader constructor-End")

    def _load_data(self, cohortId: int) -> bool:
        """Function to call the solr data loader."""
        logger.info("_load_data-Start")
        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        logger.info("solr_delete_url-Start")

        delete_data = {"delete": {"query": f"filter(cohortid:{cohortId})"}}
        logger.info(delete_data)
        delete_response = requests.post(
            self.solr_delete_url,
            data=json.dumps(delete_data),
            headers=headers,
            verify=self._certificates_path,
        )

        logger.info(f"delete_response: {delete_response}")

        if delete_response.status_code != 200:
            raise Exception(
                f"Error in API data delete call: {delete_response.status_code}, Reason: {delete_response.reason}"  # noqa: E501
            )

        logger.info("solr_delete_url-End")
        time.sleep(5)
        logger.info("solr_import_url-Start")

        load_url = f"{self.solr_import_url}{cohortId}"
        timestamp_int = int(datetime.datetime.utcnow().timestamp())
        url_time = f"{load_url}&_={timestamp_int}"

        load_response = requests.get(
            url_time, headers=headers, verify=self._certificates_path
        )
        logger.info(f"load_response: {load_response}")

        if load_response.status_code != 200:
            raise Exception(
                f"Error in API data load call: {load_response.status_code}, Reason: {load_response.reason}"  # noqa: E501
            )
        else:
            logger.info("solr_import_url-End")

            # data_load = load_response.json()
            # logger.info(f"data_load: {data_load}")

            logger.info("solr_status_url-Start")
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

    def _load_data_status(self) -> requests.Response:
        """Function to call the solr data loader."""

        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        timestamp_int = int(datetime.datetime.utcnow().timestamp())
        url_time = f"{self.solr_status_url}&_={timestamp_int}"
        response = requests.get(
            url_time,
            headers=headers,
            verify=self._certificates_path,  # noqa: E501
        )

        if response.status_code != 200:
            raise Exception(
                f"Error in API status call: {response.status_code}, Reason: {response.reason}"  # noqa: E501
            )

        return response

    def are_there_records_to_load(self, cohortId: int) -> bool:
        select_query = text(
            """SELECT count(0) From [dbo].[V_AIRFLOW_Cohort_Case_Load]"""
        )

        if cohortId != 0:
            select_query = text(
                f"""SELECT count(0) From [dbo].[V_AIRFLOW_Cohort_Case_Load] Where CohortId={cohortId}"""  # noqa: E501
            )
        record_count = self._piro_db_connection.execute(select_query).scalar()
        return True if (record_count and record_count > 0) else False

    def reset_data_for_next_load(self, cohortId: int):
        sql_update = text(
            f"EXEC [dbo].[P_Airflow_Cohort_Processed_Update] @cohort_id={cohortId}"  # noqa: E501
        )

        self._piro_db_session.execute(sql_update)
        self._piro_db_session.commit()
        return True

    def reset_is_solr_updated_flags(self) -> None:
        """
        Sets IsSolrUpdated flags to 0 for all Cohort & CohortCase records.
        """

        sql = text("""EXEC dbo.[P_Airflow_Cohort_Reload_Data]""")
        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()

    def close_db_connection(self) -> None:
        """Close any connections to the database."""

        self._piro_db_session.close()
        self._piro_db_connection.close()

    def _get_cohort_data(
        self, cohort_id: int, start_key: int, data_record_count: int
    ) -> list:
        select_query = text(f"""
            declare @queue nvarchar(max)
            select @queue = (
                Select TOP {int(float(data_record_count))} *
                from dbo.V_AIRFLOW_Cohort_Case_Load
                WHERE [id] > {start_key}
                Order by [id]
                FOR JSON PATH
            )
            select @queue as JSON
            """)
        if cohort_id != 0:
            select_query = text(f"""
                declare @queue nvarchar(max)
                select @queue = (
                    Select TOP {int(float(data_record_count))} *
                    from dbo.V_AIRFLOW_Cohort_Case_Load
                    WHERE [id] > {start_key} and [cohortid] = {cohort_id}
                    Order by [id]
                    FOR JSON PATH
                )
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

    def _get_cohort_data_key_min(self, cohort_id: int) -> int:
        select_query = text(f"""
            SELECT Min([id]) Min_id, Max([id]) Max_id
            FROM dbo.V_AIRFLOW_Cohort_Case_Load
            FOR JSON PATH
            """)
        if cohort_id != 0:
            select_query = text(f"""
                SELECT (Min([id]) - 1) Min_id, Max([id]) Max_id
                FROM dbo.V_AIRFLOW_Cohort_Case_Load
                WHERE [cohortid] = {cohort_id}
                FOR JSON PATH
                """)
        data = self._piro_db_connection.execute(select_query).scalar()
        try:
            dataJson = json.loads(data)
            if len(dataJson) > 0:
                return dataJson[0]["Min_id"]
        except json.JSONDecodeError:
            return None

    def upload_records_to_solr(self, cohort_id: int) -> bool:
        """Function to call the solr data loader."""
        key = self._get_cohort_data_key_min(cohort_id)
        if key is None:
            return None

        data_record_count: int = self.solr_update_batch
        process_data: bool = True
        retry_index: int = 0
        while process_data:
            logger.info(f"key: {key}")
            data = self._get_cohort_data(cohort_id, key, data_record_count)
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
            logger.info(f"response: {response.status_code}")

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
                key = data[-1]["id"]
                data_record_count: int = self.solr_update_batch
                retry_index = 0

        return True
