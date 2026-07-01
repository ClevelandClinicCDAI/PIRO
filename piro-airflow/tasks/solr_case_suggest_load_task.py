"""
Airflow tasks for loading case number 'suggest' data into SOLR.
"""

from airflow.sdk import task
from tasks.loaders.solr_case_suggest_loader import SolrCaseSuggestLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var, set_var

logger = get_logger()


@task
def solr_case_number_suggest_load_task():
    """Load case number 'suggest' data into Solr."""

    loader = SolrCaseSuggestLoader()
    there_are_records_to_load = loader.are_there_records_to_load()

    if there_are_records_to_load:
        loader.upload_records_to_solr()
        loader.reset_data_for_next_load()
        loader.close_db_connection()
    else:
        loader.close_db_connection()
        logger.info("No case number 'suggest' data to load; skipping.")


@task
def solr_case_number_suggest_queue_reload_task():
    """Truncate and reload Solr staging tables so that all case number
    'suggest' records will be reset on the next load."""

    should_reload_case_number_suggest_data = get_var(
        "SOLR_CASE_SUGGEST_DB_RELOAD_DATA"
    )
    if should_reload_case_number_suggest_data == "1":
        loader = SolrCaseSuggestLoader()
        loader.reset_solr_staging_tables()
        loader.close_db_connection()
        set_var("SOLR_CASE_SUGGEST_DB_RELOAD_DATA", "0")
    else:
        raise Exception(
            "SOLR_CASE_SUGGEST_DB_RELOAD_DATA has to be set to 1 to run this job."  # noqa:E501
        )
