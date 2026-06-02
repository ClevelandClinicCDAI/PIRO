"""
Airflow task for loading the cohort case mapping data into SOLR.

Original version created on Tue Jul 09 10:50:21 2024
@author: Ven
"""

from airflow.sdk import task
from tasks.loaders.ssis_data_job_loader import SsisDataJobLoader
from tasks.utils.logging_setup import get_logger

logger = get_logger()


@task
def ssis_delta_load_job_task():
    loader = SsisDataJobLoader()
    loader.run_delta_load()
    loader.close_db_connection()


@task
def ssis_full_load_task():
    loader = SsisDataJobLoader()
    loader.run_full_load()
    loader.close_db_connection()
