"""
Airflow task for loading the cohort case mapping data into SOLR.

Original version created on Tue Jul 09 10:50:21 2024
@author: Ven
"""

from airflow.decorators import task
from tasks.loaders.solr_cohort_data_loader import SolrCohortDataLoader
from tasks.utils.logging_setup import get_logger
from airflow.operators.python import get_current_context

from tasks.utils.solr_setup import get_solr_cohort_db_reload_data
from tasks.utils.variable_setup import set_var

logger = get_logger()


@task
def solr_cohort_data_load_task(ti):
    is_trigger = ti.xcom_pull(key="is_trigger")  # noqa: E501
    logger.info(f"is_trigger xcom pull: {is_trigger}")
    if is_trigger:
        cohort_Id = get_context_param_cohort_id()

        logger.info("solr_cohort_data_load_task-Start")
        loader = SolrCohortDataLoader()
        isProcessed = loader._upload_data_solr(cohort_id=cohort_Id)
        logger.info(f"isProcessed: {isProcessed}")
        if isProcessed:
            logger.info("_reset_cohort_data-Start")
            loader._reset_cohort_data(cohortId=cohort_Id)
            logger.info("_reset_cohort_data-End")
        loader._close_db_connection()
        logger.info("solr_cohort_data_load_task-End")
    else:
        logger.info("solr_cohort_data_load_task-Skipped")


@task
def solr_cohort_data_load_check_trigger_task(ti):

    logger.info("solr_cohort_data_load_check_trigger_task-Start")
    cohort_Id = get_context_param_cohort_id()

    loader = SolrCohortDataLoader()
    is_trigger = loader._get_trigger_to_process(cohortId=cohort_Id)
    loader._close_db_connection()
    logger.info(
        f"solr_cohort_data_load_check_trigger_task-is_trigger: {is_trigger}"
    )  # noqa: E501
    logger.info(f"is_trigger xcom push: {is_trigger}")
    ti.xcom_push(key="is_trigger", value=is_trigger)
    logger.info("solr_cohort_data_load_check_trigger_task-End")


@task
def solr_cohort_data_load_update_trigger_task(ti):
    logger.info("solr_cohort_data_load_update_trigger_task-Start")
    logger.info("solr_cohort_data_load_update_trigger_task-End")


def get_context_param_cohort_id() -> int:
    context = get_current_context()

    if context is None:
        raise Exception("Context is Null")
    cohort_Id: int = None
    if "params" in context and "cohortId" in context["params"]:
        cohort_Id = context["params"]["cohortId"]
        logger.info(f"Cohort Single load. cohort_Id passed: {cohort_Id}")
    else:
        cohort_Id = 0
        logger.info("Cohort bulk loading")

    return cohort_Id


@task
def solr_cohort_db_reload_task(ti):
    is_trigger = get_solr_cohort_db_reload_data()
    logger.info(f"is_trigger (SOLR_COHORT_DB_RELOAD_DATA)): {is_trigger}")
    if is_trigger == "1":
        logger.info("solr_cohort_db_reload_task-Start")
        loader = SolrCohortDataLoader()
        loader._reload_sql_case_data()
        loader._close_db_connection()
        set_var("SOLR_COHORT_DB_RELOAD_DATA", "0")
        logger.info("SOLR_COHORT_DB_RELOAD_DATA-Reset to 0")
        logger.info("solr_cohort_db_reload_task-End")
    else:
        logger.error("solr_cohort_db_reload_task-Skipped")
        raise Exception(
            "SOLR_COHORT_DB_RELOAD_DATA has to be set to 1 to run this job"
        )
