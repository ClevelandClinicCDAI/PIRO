"""Master DAG configuration file for the 'piro-airflow' project."""

import pendulum
from airflow.decorators import dag
from airflow.models import Variable
from tasks.rtf_to_plain_text_task import rtf_to_plain_text_task
from tasks.malignant_annotation_task import malignant_annotation_task
from tasks.solr_cohort_data_load_task import (
    solr_cohort_data_load_task,
    solr_cohort_data_load_check_trigger_task,
    solr_cohort_data_load_update_trigger_task,
    solr_cohort_db_reload_task,
)
from tasks.solr_case_data_load_task import (
    solr_case_data_load_task,
    solr_case_db_reload_task,
    solr_case_reset_task,
    solr_case_check_trigger_task,
    solr_case_update_trigger_task,
)
from tasks.solr_cohort_data_delete_task import (
    solr_cohort_data_delete_task,
    solr_cohort_data_delete_check_trigger_task,
    solr_cohort_data_delete_update_trigger_task,
)
from tasks.solr_case_suggest_load_task import (
    solr_case_suggest_db_reload_task,
    solr_case_suggest_load_task,
    solr_case_suggest_check_trigger_task,
    solr_case_suggest_reset_task,
    solr_case_suggest_update_trigger_task,
)
from tasks.solr_case_staff_load_task import (
    solr_case_staff_load_task,
    solr_case_staff_check_trigger_task,
    solr_case_staff_reset_task,
    solr_case_staff_update_trigger_task,
    solr_case_staff_db_reload_task,
)
from tasks.ssis_data_load_task import (
    ssis_delta_load_job_task,
    ssis_full_load_job_task,
)
from tasks.utils.logging_setup import get_logger

logger = get_logger()
DEVELOPER_EMAILS = [
    "[developer email(s)]",
]


@dag(
    description=(
        "DAG for creating annotations from case text in the PIRO database."
    ),
    schedule_interval="0 0 * * *",  # Midnight Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SQL", "Annotation"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_annotations():
    # tasks to execute
    rtf_to_plain_text = rtf_to_plain_text_task()
    malignant_annotation = malignant_annotation_task()

    # dependency definitions
    rtf_to_plain_text >> malignant_annotation


###############################################################################
@dag(
    description="DAG for creating cohort case mapping in the SOLR",
    schedule_interval="15 6 * * *",  # 6:15AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SOLR", "Cohort", "ADD"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_cohort_data():
    solr_cohort_data_load_check_trigger = (
        solr_cohort_data_load_check_trigger_task()
    )
    solr_cohort_data_load = solr_cohort_data_load_task()
    solr_cohort_data_load_update_trigger = (
        solr_cohort_data_load_update_trigger_task()
    )

    (
        solr_cohort_data_load_check_trigger
        >> solr_cohort_data_load
        >> solr_cohort_data_load_update_trigger
    )


###############################################################################
@dag(
    description=("DAG for reloading cohort data in the PIRO database."),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SQL", "Cohort"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_cohort_db_reload_data():
    # tasks to execute
    solr_cohort_db_reload_task_ = solr_cohort_db_reload_task()
    # dependency definitions
    solr_cohort_db_reload_task_


###############################################################################
@dag(
    description=("DAG for reloading case data in the PIRO database."),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SQL", "CASE"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_db_reload_data():
    # tasks to execute
    solr_case_clear_task = solr_case_db_reload_task()
    # dependency definitions
    solr_case_clear_task


###############################################################################
@dag(
    description="DAG for deleting cohort case mapping in the SOLR",
    schedule_interval="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SOLR", "Cohort", "DELETE"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_cohort_delete():
    solr_cohort_data_delete_check_trigger = (
        solr_cohort_data_delete_check_trigger_task()
    )
    solr_cohort_data_delete = solr_cohort_data_delete_task()
    solr_cohort_data_delete_update_trigger = (
        solr_cohort_data_delete_update_trigger_task()
    )

    (
        solr_cohort_data_delete_check_trigger
        >> solr_cohort_data_delete
        >> solr_cohort_data_delete_update_trigger
    )


###############################################################################
@dag(
    description="DAG for running the full data import of the case data in the SOLR",  # noqa: E501
    schedule_interval="0 6 * * *",  # 6AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SOLR", "Case"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_data():
    solr_case_check_trigger = solr_case_check_trigger_task()
    solr_case_data_load = solr_case_data_load_task()
    solr_case_update = solr_case_reset_task()
    solr_case_update_trigger = solr_case_update_trigger_task()

    (
        solr_case_check_trigger
        >> solr_case_data_load
        >> solr_case_update
        >> solr_case_update_trigger
    )


###############################################################################
@dag(
    description="DAG for running the full data import of the case suggestions in the SOLR",  # noqa: E501
    schedule_interval="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SOLR", "CaseSuggest"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_suggest():
    solr_case_suggest_check_trigger = solr_case_suggest_check_trigger_task()
    solr_case_suggest_load = solr_case_suggest_load_task()
    solr_case_suggest_reset = solr_case_suggest_reset_task()
    solr_case_suggest_update_trigger = solr_case_suggest_update_trigger_task()

    (
        solr_case_suggest_check_trigger
        >> solr_case_suggest_load
        >> solr_case_suggest_reset
        >> solr_case_suggest_update_trigger
    )


###############################################################################
@dag(
    description=("DAG for reloading case suggest data in the PIRO database."),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SQL", "CaseSuggest"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_suggest_db_reload_data():
    # tasks to execute
    solr_case_suggest_clear_task = solr_case_suggest_db_reload_task()
    # dependency definitions
    solr_case_suggest_clear_task


###############################################################################
@dag(
    description="DAG for running the full data import of the case suggestions in SOLR",  # noqa: E501
    schedule_interval="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SOLR", "CaseStaff"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_staff():
    solr_case_staff_check_trigger = solr_case_staff_check_trigger_task()
    solr_case_staff_load = solr_case_staff_load_task()
    solr_case_staff_reset = solr_case_staff_reset_task()
    solr_case_staff_update_trigger = solr_case_staff_update_trigger_task()

    (
        solr_case_staff_check_trigger
        >> solr_case_staff_load
        >> solr_case_staff_reset
        >> solr_case_staff_update_trigger
    )


###############################################################################
@dag(
    description=("DAG for reloading case staff data in the PIRO database."),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SQL", "CaseStaff"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def piro_case_staff_db_reload_data():
    # tasks to execute
    solr_case_staff_db_reload_task_ = solr_case_staff_db_reload_task()
    # dependency definitions
    solr_case_staff_db_reload_task_


###############################################################################
ssis_delta_schedule: str = Variable.get(
    "SSIS_DELTA_LOAD_JOB_SCHEDULE", "30 16 * * *"
)


@dag(
    description=(
        "DAG for triggering the delta data load job in the PIRO SSIS database."
    ),
    schedule_interval=ssis_delta_schedule,  # See Airflow Vars
    start_date=pendulum.datetime(2025, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["PIRO", "SSIS", "Delta Load"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def ssis_delta_load_job():

    # tasks to execute
    ssis_delta_load_job_task_ = ssis_delta_load_job_task()
    # dependency definitions
    ssis_delta_load_job_task_


###############################################################################
@dag(
    description=(
        "DAG for triggering the full data load job in the PIRO SSIS database."
    ),
    start_date=pendulum.datetime(2025, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["PIRO", "SSIS", "Full Load"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def ssis_full_load_job():
    # tasks to execute
    ssis_full_load_job_task_ = ssis_full_load_job_task()
    # dependency definitions
    ssis_full_load_job_task_


# Function calls
piro_annotations()

piro_cohort_data()

piro_case_suggest()

piro_case_staff()

piro_cohort_delete()

piro_case_data()

piro_case_db_reload_data()

piro_case_suggest_db_reload_data()

piro_case_staff_db_reload_data()

piro_cohort_db_reload_data()

ssis_delta_load_job()

ssis_full_load_job()
