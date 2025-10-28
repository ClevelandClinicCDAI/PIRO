"""
Airflow task for loading the cohort case mapping data into SOLR.

Original version created on Tue Jul 09 10:50:21 2024
@author: Ven
"""

from airflow.decorators import task
from tasks.loaders.ssis_data_job_loader import SsisDataJobLoader
from tasks.utils.logging_setup import get_logger

logger = get_logger()


@task
def ssis_delta_load_job_task(ti):
    logger.info("ssis_delta_load_job_task-Start")
    loader = SsisDataJobLoader()
    logger.info("loader._run_delta_load_job-Start")
    loader._run_delta_load_job()
    logger.info("loader._run_delta_load_job-End")
    loader._close_db_connection()
    logger.info("ssis_delta_load_job_task-End")


@task
def ssis_full_load_job_task(ti):
    logger.info("ssis_full_load_job_task-Start")
    loader = SsisDataJobLoader()
    loader._run_full_load_job()
    loader._close_db_connection()
    logger.info("ssis_full_load_job_task-End")
