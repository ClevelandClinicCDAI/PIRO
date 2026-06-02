"""
Airflow tasks for loading staff 'suggest' data into SOLR.
"""

from airflow.sdk import task
from tasks.loaders.solr_case_staff_loader import SolrCaseStaffLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var, set_var

logger = get_logger()


@task
def solr_staff_suggest_load_task():
    """Load staff 'suggest' data into Solr."""

    loader = SolrCaseStaffLoader()
    there_are_records_to_load: bool = loader.are_there_records_to_load()

    if there_are_records_to_load:
        loader.upload_records_to_solr()
        loader.reset_data_for_next_load()
        loader.close_db_connection()
    else:
        loader.close_db_connection()
        logger.info("No staff 'suggest' data to load; skipping.")


@task
def solr_staff_suggest_queue_reload_task():
    """Reset data in staging tables so that all staff 'suggest' data
    in Solr will be reset on the next load."""

    should_reload_staff_suggest_data = get_var(
        "SOLR_CASE_STAFF_DB_RELOAD_DATA"
    )
    if should_reload_staff_suggest_data == "1":
        loader = SolrCaseStaffLoader()
        loader.delete_staff_suggest_staging_data()
        loader.close_db_connection()
        set_var("SOLR_CASE_STAFF_DB_RELOAD_DATA", "0")
    else:
        raise Exception(
            "SOLR_CASE_STAFF_DB_RELOAD_DATA has to be set to 1 to run this task."  # noqa:E501
        )
