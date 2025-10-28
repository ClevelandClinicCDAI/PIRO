"""
Airflow task for loading the full import of the case data into SOLR.
The data is loaded from the dbo.V_SOLR_Case_Delta that contains the delta
records.

Original version created on Tue Jul 09 10:50:21 2024
@author: Ven
"""

from airflow.decorators import task
from tasks.loaders.solr_case_staff_loader import SolrCaseStaffLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.solr_setup import get_solr_case_staff_db_reload_data
from tasks.utils.variable_setup import set_var

logger = get_logger()


@task
def solr_case_staff_load_task(ti):
    is_trigger = ti.xcom_pull(key="is_trigger")  # noqa: E501
    logger.info(f"is_trigger xcom pull: {is_trigger}")
    if is_trigger:
        logger.info("solr_case_staff_load_task-Start")
        loader = SolrCaseStaffLoader()
        loader._upload_data_solr()
        logger.info("solr_case_staff_load_task-End")
    else:
        logger.info("solr_case_staff_load_task-Skipped")


@task
def solr_case_staff_check_trigger_task(ti):
    logger.info("solr_case_staff_check_trigger_task-Start")

    loader = SolrCaseStaffLoader()
    is_trigger = loader._get_trigger_to_process()
    loader._close_db_connection()
    logger.info(f"solr_case_staff_check_trigger_task-is_trigger: {is_trigger}")
    logger.info(f"is_trigger xcom push: {is_trigger}")
    ti.xcom_push(key="is_trigger", value=is_trigger)
    logger.info("solr_case_staff_check_trigger_task-End")


@task
def solr_case_staff_reset_task(ti):
    is_trigger = ti.xcom_pull(key="is_trigger")  # noqa: E501
    logger.info(f"is_trigger xcom pull: {is_trigger}")
    if is_trigger:
        logger.info("solr_case_staff_update_task-Start")
        loader = SolrCaseStaffLoader()
        loader._reset_case_staff_data()
        loader._close_db_connection()
        logger.info("solr_case_staff_update_task-End")
    else:
        logger.info("solr_case_staff_update_task-Skipped")


@task
def solr_case_staff_update_trigger_task(ti):
    logger.info("solr_case_staff_update_trigger_task-Start")
    logger.info("solr_case_staff_update_trigger_task-End")


@task
def solr_case_staff_db_reload_task(ti):
    is_trigger = get_solr_case_staff_db_reload_data()
    logger.info(f"is_trigger (SOLR_CASE_STAFF_DB_RELOAD_DATA)): {is_trigger}")
    if is_trigger == "1":
        logger.info("solr_case_staff_db_reload_task-Start")
        loader = SolrCaseStaffLoader()
        loader._reload_sql_case_data()
        loader._close_db_connection()
        set_var("SOLR_CASE_STAFF_DB_RELOAD_DATA", "0")
        logger.info("SOLR_CASE_STAFF_DB_RELOAD_DATA-Reset to 0")
        logger.info("solr_case_staff_db_reload_task-End")
    else:
        logger.error("solr_case_staff_db_reload_task-Skipped")
        raise Exception(
            "SOLR_CASE_STAFF_DB_RELOAD_DATA has to be set to 1 to run this job"
        )
