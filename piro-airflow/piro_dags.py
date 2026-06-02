"""Master DAG configuration file for the 'piro-airflow' project."""

import pendulum
from airflow.sdk import dag, Variable
from tasks.rtf_to_plain_text_task import rtf_to_plain_text_task
from tasks.malignant_annotation_task import malignant_annotation_task
from tasks.solr_cohort_data_delete_task import solr_cohort_delete_task
from tasks.solr_cohort_data_load_task import (
    solr_cohort_load_task,
    solr_cohort_queue_reload_task,
)
from tasks.solr_case_data_load_task import (
    solr_case_load_task,
    solr_case_queue_reload_task,
)
from tasks.solr_case_suggest_load_task import (
    solr_case_number_suggest_queue_reload_task,
    solr_case_number_suggest_load_task,
)
from tasks.solr_case_staff_load_task import (
    solr_staff_suggest_load_task,
    solr_staff_suggest_queue_reload_task,
)
from tasks.concentriq_case_load_task import (
    concentriq_load_task,
    concentriq_reset_task,
)
from tasks.ssis_data_load_task import (
    ssis_delta_load_job_task,
    ssis_full_load_task,
)
from tasks.utils.logging_setup import get_logger

logger = get_logger()
DEVELOPER_EMAILS = [
    "cumboj@ccf.org",
]


@dag(
    description=(
        "DAG for creating annotations from case text in the PIRO database."
    ),
    schedule="0 0 * * *",  # Midnight Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Annotation"],
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
    rtf_to_plain_text >> malignant_annotation  # type: ignore


###############################################################################
@dag(
    description="DAG for loading cohort and cohort-case data into Solr.",
    schedule="15 6 * * *",  # 6:15AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Solr", "Cohort"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_cohort_load():
    solr_cohort_load_task()


###############################################################################
@dag(
    description=("""DAG for queuing up a reload of cohort data in Solr.

        This DAG does not update Solr, it updates the PIRO database so that
        the next run of the load task will reload all records.
        """),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Solr", "Cohort"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_cohort_queue_reload():

    solr_cohort_queue_reload_task()


###############################################################################
@dag(
    description=("""DAG for deleting cohort data in Solr.

        This DAG ensures that, if a cohort is deleted in the PIRO database, it
        will also be deleted in Solr."""),
    schedule="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Solr", "Cohort", "DELETE"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_cohort_delete():

    solr_cohort_delete_task()


###############################################################################
@dag(
    description="DAG for loading case data into Solr.",
    schedule="0 6 * * *",  # 6AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Solr", "Case"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_case_load():

    solr_case_load_task()


###############################################################################
@dag(
    description=("""DAG for queuing up a reload of case data in Solr.

        This DAG does not update Solr, it updates the PIRO database so that
        the next run of the load task will reload all records.
        """),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Solr", "Case"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_case_queue_reload():

    solr_case_queue_reload_task()


###############################################################################
@dag(
    description=("""DAG for loading case 'suggest' data into Solr.

        The case 'suggest' data is used in the PIRO user interface. When the user
        selects 'Case Number' from the drop-down menu in the main search box
        and begins typing, case numbers from this Solr index will be used to
        present the user with auto-complete options."""),  # noqa: E501
    schedule="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Solr", "CaseSuggest"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_case_number_suggest_load():

    solr_case_number_suggest_load_task()


###############################################################################
@dag(
    description=("""DAG for queuing up a reload of case 'suggest' data in Solr.

        This DAG does not update Solr, it updates the PIRO database so that
        the next run of the load task will reload all records."""),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Solr", "CaseSuggest"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_case_number_suggest_queue_reload():

    solr_case_number_suggest_queue_reload_task()


###############################################################################
@dag(
    description=(""""DAG for loading staff 'suggest' data into Solr.

        The staff 'suggest' data is used in the PIRO user interface. When the
        user selects 'Pathologist' from the drop-down menu in the main search
        box and begins typing, staff names from this Solr index will be used to
        present the user with auto-complete options."""),
    schedule="30 6 * * *",  # 6:30AM Eastern Daily
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Solr", "CaseStaff"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_staff_suggest_load():

    solr_staff_suggest_load_task()


###############################################################################
@dag(
    description=(
        """DAG for queuing up a reload of staff 'suggest' data in Solr.

        This DAG does not update Solr, it updates the PIRO database so that
        the next run of the load task will reload all records."""
    ),
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Solr", "CaseStaff"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def solr_staff_suggest_queue_reload():

    solr_staff_suggest_queue_reload_task()


###############################################################################
@dag(
    description="DAG for loading Concentriq data into PIRO.",
    schedule="30 12 * * *",  # 12:30AM Eastern Daily
    start_date=pendulum.datetime(2025, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["Concentriq"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def concentriq_load():

    concentriq_load_task()


###############################################################################
@dag(
    description="DAG for deleting concentriq data in the PIRO database.",
    start_date=pendulum.datetime(2024, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["Concentriq"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def concentriq_reset():

    concentriq_reset_task()


###############################################################################
ssis_delta_schedule: str = Variable.get(
    "SSIS_DELTA_LOAD_JOB_SCHEDULE", "30 16 * * *"
)


@dag(
    description=(
        "DAG for triggering the delta data load job in the PIRO SSIS database."
    ),
    schedule=ssis_delta_schedule,  # See Airflow Vars
    start_date=pendulum.datetime(2025, 1, 1, tz="US/Eastern"),
    max_active_runs=5,
    catchup=False,
    tags=["SSIS", "Delta Load"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def ssis_delta_load():

    ssis_delta_load_job_task()


###############################################################################
@dag(
    description=(
        "DAG for triggering the full data load job in the PIRO SSIS database."
    ),
    start_date=pendulum.datetime(2025, 1, 1, tz="US/Eastern"),
    max_active_runs=1,
    catchup=False,
    tags=["SSIS", "Full Load"],
    default_args={
        "email": DEVELOPER_EMAILS,
        "email_on_failure": True,
    },
)
def ssis_full_load():

    ssis_full_load_task()


# DAG Instantiation
piro_annotations()
solr_cohort_load()
solr_cohort_queue_reload()
solr_cohort_delete()
solr_case_load()
solr_case_queue_reload()
solr_case_number_suggest_load()
solr_case_number_suggest_queue_reload()
solr_staff_suggest_load()
solr_staff_suggest_queue_reload()
concentriq_load()
concentriq_reset()
ssis_delta_load()
ssis_full_load()
