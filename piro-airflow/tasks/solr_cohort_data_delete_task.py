from airflow.sdk import task
from tasks.loaders.solr_cohort_data_delete import SolrCohortDataDelete
from tasks.utils.logging_setup import get_logger

logger = get_logger()


@task
def solr_cohort_delete_task():
    """
    Airflow task for deleting cohort data in SOLR.

    This task ensures that, if a cohort is deleted in the PIRO database, it
    will also be deleted in Solr."""
    loader = SolrCohortDataDelete()
    should_delete_records: bool = loader.should_we_delete_records()
    if should_delete_records:
        loader.delete_data()
        loader.close_db_connection()
    else:
        logger.info("Skipping deletion of cohort records in Solr.")
