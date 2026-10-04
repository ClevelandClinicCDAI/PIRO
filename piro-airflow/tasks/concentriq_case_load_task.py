"""
Airflow task for loading the cases from Concentriq into PIRO.
Each successful run reconciles the complete PostgreSQL image catalog.
"""

from airflow.sdk import task
from tasks.loaders.concentriq_case_loader import ConcentriqCaseLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.concentriq_setup import get_concentriq_case_db_reload_data
from tasks.utils.variable_setup import set_var

logger = get_logger()


@task
def concentriq_load_task():
    """Load cases from Concentriq into PIRO.

    Checks whether there are records to process and, if so, fetches the data
    from Concentriq and processes it into the PIRO database.
    """
    loader = ConcentriqCaseLoader()
    try:
        if loader.should_we_process_concentriq_data():
            loader.get_concentriq_data()
        else:
            logger.info("Concentriq configuration not set up to allow loading.")
    finally:
        loader.close_db_connection()


@task
def concentriq_reset_task():
    """Deletes all Concentriq data in the PIRO database so that it can be
    reloaded."""

    should_delete_concentriq_data = get_concentriq_case_db_reload_data()
    if should_delete_concentriq_data == 1:
        loader = ConcentriqCaseLoader()
        try:
            loader.delete_concentriq_case_data()
        finally:
            loader.close_db_connection()
        set_var("CONCENTRIQ_CASE_DB_RELOAD_DATA", "0")
    else:
        raise Exception(
            "CONCENTRIQ_CASE_DB_RELOAD_DATA has to be set to 1 to run this job."  # noqa:E501
        )
