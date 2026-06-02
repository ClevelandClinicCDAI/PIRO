import json
import requests
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from sqlalchemy import text
from tasks.utils.database_setup import get_piro_db_engine, get_piro_db_session
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_certificate_path_solr
from tasks.utils.solr_setup import get_solr_cohort_data_update_url
from tasks.utils.solr_setup import get_solr_header_auth

logger = get_logger()


class SolrCohortDataDelete:
    """Class for deleting case data into SOLR. The source data table is CohortCase_Delta. SOLR delete job is triggered"""  # noqa: E501

    def __init__(self):
        logger.info("SolrCohortDataDelete constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )

        self._authentication_header = get_solr_header_auth()
        self.solr_delete_url = get_solr_cohort_data_update_url()

        self._certificates_path: str = get_certificate_path_solr()
        logger.info(f"self._certificates_path: {self._certificates_path}")
        logger.info(f"self.solr_delete_url: {self.solr_delete_url}")
        logger.info("SolrCohortDataDelete constructor-End")

    def delete_data(self) -> bool:
        logger.info("_delete_data-Start")

        records_to_delete: list[Row] = self._get_records_to_delete()

        for record in records_to_delete:
            cohortId = record[0]
            logger.info(f"cohortId: {cohortId}")
            self.delete_solr_data(cohortId=cohortId)
            logger.info(f"delete_solr_data: {cohortId}")
            self._reset_cohort_data(cohortId=cohortId)
            logger.info(f"_reset_cohort_data: {cohortId}")

        logger.info("_delete_data-End")
        return True

    def delete_solr_data(self, cohortId: int) -> bool:
        """Function to call the solr data loader."""

        headers = {
            "Authorization": f"Basic {self._authentication_header}",
            "Content-Type": "application/json",
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

        return True

    def _get_records_to_delete(self) -> list[Row]:
        """Query the V_SOLR_Cohort_Delete_Load view for records to be deleted in SOLR."""  # noqa: E501
        select_query = text(
            """SELECT [CohortId] From [dbo].[V_SOLR_Cohort_Delete_Load]"""
        )
        return self._piro_db_connection.execute(select_query).fetchall()

    def should_we_delete_records(self) -> bool:
        """Query the V_SOLR_Cohort_Delete_Load view to determine if records
        should be deleted in SOLR."""

        select_query = text(
            """SELECT count(0) From [V_AIRFLOW_Cohort_Delete_Load]"""
        )
        recordCount = self._piro_db_connection.execute(select_query).scalar()
        return True if (recordCount and recordCount > 0) else False

    def _reset_cohort_data(self, cohortId: int):
        sql = text(f"""EXEC [P_Airflow_Cohort_Processed_Update] {cohortId}""")

        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        return True

    def close_db_connection(self) -> None:
        """Close any connections to the database."""
        self._piro_db_session.close()
        self._piro_db_connection.close()
