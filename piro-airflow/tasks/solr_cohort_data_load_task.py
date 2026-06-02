"""
Airflow tasks for loading the cohort case data into SOLR.
"""

from airflow.sdk import task, get_current_context

from tasks.loaders.solr_cohort_data_loader import SolrCohortDataLoader
from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var, set_var

logger = get_logger()


@task
def solr_cohort_load_task():
    """Load CohortCase data into Solr."""

    context = get_current_context()
    cohort_id = get_cohort_id(context)
    loader = SolrCohortDataLoader()

    there_are_records_to_load: bool = loader.are_there_records_to_load(
        cohortId=cohort_id
    )

    try:
        if there_are_records_to_load:
            load_result: bool = loader.upload_records_to_solr(
                cohort_id=cohort_id
            )
            if load_result:
                loader.reset_data_for_next_load(cohortId=cohort_id)
        else:
            logger.info("No Cohort data to load; skipping.")
    finally:
        loader.close_db_connection()


def get_cohort_id(context) -> int:
    """Return the cohort ID for the DAG run, if specified; otherwise 0.

    By convention, a value of 0 (the default) implies that data for all
    cohorts should be loaded.

    The 'piro-api' codebase will make an HTTP request to the Airflow API
    when a cohort is created or updated, and when it does so, a Cohort ID
    will be provided."""

    cohort_Id: int = 0
    if "params" in context and "cohortId" in context["params"]:
        cohort_Id = context["params"]["cohortId"]

    return cohort_Id


@task
def solr_cohort_queue_reload_task():
    """Reset database flags so that all cohort data in Solr will be reset on
    the next load."""

    should_reload_cohort_data: str = get_var("SOLR_COHORT_DB_RELOAD_DATA")
    if should_reload_cohort_data == "1":
        loader = SolrCohortDataLoader()
        loader.reset_is_solr_updated_flags()
        loader.close_db_connection()
        set_var("SOLR_COHORT_DB_RELOAD_DATA", "0")
    else:
        raise Exception(
            "SOLR_COHORT_DB_RELOAD_DATA has to be set to 1 to run this job"
        )
