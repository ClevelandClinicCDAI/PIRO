"""
Airflow tasks for loading case data into SOLR.
"""

from airflow.sdk import task
from tasks.loaders.solr_case_data_loader import SolrCaseDataLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var, set_var

logger = get_logger()


@task
def solr_case_load_task():
    """Load case data into Solr.

    Checks whether there are records to process and, if so, uploads the data
    and resets the case data flags in the database.
    """
    loader = SolrCaseDataLoader()
    there_are_records_to_load = loader.are_there_records_to_load()

    if there_are_records_to_load:
        loader.upload_records_to_solr()
        loader.reset_data_for_next_load()
        loader.close_db_connection()
    else:
        loader.close_db_connection()
        logger.info("No case data to load; skipping.")


@task
def solr_case_queue_reload_task():
    """Delete case data from the solr staging tables in the PIRO database so
    that it can be reloaded.

    Note that this task does not delete data from the main case tables in the
    PIRO database; only the tables used to load Solr.
    """

    should_reload_case_data = get_var("SOLR_CASE_DB_RELOAD_DATA")
    if should_reload_case_data == "1":
        loader = SolrCaseDataLoader()
        loader.delete_solr_staging_data()
        loader.close_db_connection()
        set_var("SOLR_CASE_DB_RELOAD_DATA", "0")
    else:
        raise Exception(
            "Airflow variable 'SOLR_CASE_DB_RELOAD_DATA' has to be set to 1 to run this job."  # noqa:E501
        )
