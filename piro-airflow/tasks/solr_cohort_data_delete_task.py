"""
Airflow task for deleting the cohort case mapping data in SOLR.

Original version created on Tue Jul 09 10:50:21 2024
@author: Ven
"""

from airflow.decorators import task
from tasks.loaders.solr_cohort_data_delete import SolrCohortDataDelete
from tasks.utils.logging_setup import get_logger


logger = get_logger()


@task
def solr_cohort_data_delete_task(ti):
    is_trigger = ti.xcom_pull(key="is_trigger")   # noqa: E501
    logger.info(f"is_trigger xcom pull: {is_trigger}")
    if is_trigger:
        logger.info("solr_cohort_data_delete_task-Start")
        loader = SolrCohortDataDelete()
        loader._delete_data()
        loader._close_db_connection()
        logger.info("solr_cohort_data_delete_task-End")
    else:
        logger.info("solr_cohort_data_delete_task-Skipped")


@task
def solr_cohort_data_delete_check_trigger_task(ti):
    logger.info("solr_cohort_data_delete_check_trigger_task-Start")
    loader = SolrCohortDataDelete()
    is_trigger = loader._get_trigger_to_process()
    loader._close_db_connection()
    logger.info(f"is_trigger xcom push: {is_trigger}")
    ti.xcom_push(key="is_trigger", value=is_trigger)
    logger.info("solr_cohort_data_delete_check_trigger_task-End")


@task
def solr_cohort_data_delete_update_trigger_task(ti):
    logger.info("solr_cohort_data_delete_update_trigger_task-Start")
    logger.info("solr_cohort_data_delete_update_trigger_task-End")
