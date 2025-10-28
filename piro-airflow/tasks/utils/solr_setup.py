from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var


logger = get_logger()


def get_solr_header_auth() -> str:
    return get_var("SOLR_HEADER_AUTH")


def get_solr_case_data_import_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_IMPORT")


def get_solr_case_data_update_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_UPDATE")


def get_solr_case_data_update_batch() -> int:
    # return get_var("SOLR_CASE_BATCH_DATA_UPDATE")
    try:
        num = int(get_var("SOLR_CASE_BATCH_DATA_UPDATE"))
        return num
    except TypeError:
        logger.log(
            "Invalid input: SOLR_CASE_BATCH_DATA_UPDATE convert to integer"
        )


def get_solr_case_status_url() -> str:
    return get_var("SOLR_CASE_URL_STATUS")


def get_solr_case_db_reload_data() -> str:
    return get_var("SOLR_CASE_DB_RELOAD_DATA")


def get_solr_case_data_count_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_COUNT")


def get_solr_case_suggest_data_import_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_IMPORT")


def get_solr_case_suggest_data_update_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_UPDATE")


def get_solr_case_suggest_data_update_batch() -> int:
    # return get_var("SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE")
    try:
        num = int(get_var("SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE"))
        return num
    except TypeError:
        logger.log(
            (
                "Invalid input: SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE "
                "convert to integer"
            )
        )


def get_solr_case_suggest_status_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_STATUS")


def get_solr_case_suggest_data_count_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_COUNT")


def get_solr_case_suggest_db_reload_data() -> str:
    return get_var("SOLR_CASE_SUGGEST_DB_RELOAD_DATA")


def get_solr_case_staff_data_import_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_DATA_IMPORT")


def get_solr_case_staff_data_update_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_DATA_UPDATE")


def get_solr_case_staff_db_reload_data() -> str:
    return get_var("SOLR_CASE_STAFF_DB_RELOAD_DATA")


def get_solr_case_staff_data_update_batch() -> int:
    # return get_var("SOLR_CASE_STAFF_BATCH_DATA_UPDATE")
    try:
        num = int(get_var("SOLR_CASE_STAFF_BATCH_DATA_UPDATE"))
        return num
    except TypeError:
        logger.log(
            (
                "Invalid input: SOLR_CASE_STAFF_BATCH_DATA_UPDATE "
                "convert to integer"
            )
        )


def get_solr_case_staff_status_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_STATUS")


def get_solr_cohort_data_update_url() -> str:
    return get_var("SOLR_COHORT_URL_DATA_UPDATE")


def get_solr_cohort_data_import_url() -> str:
    return get_var("SOLR_COHORT_URL_DATA_IMPORT")


def get_solr_cohort_status_url() -> str:
    return get_var("SOLR_COHORT_URL_STATUS")


def get_solr_cohort_data_update_batch() -> int:
    # return get_var("SOLR_COHORT_BATCH_DATA_UPDATE")
    try:
        num = int(get_var("SOLR_COHORT_BATCH_DATA_UPDATE"))
        return num
    except TypeError:
        logger.log(
            "Invalid input: SOLR_COHORT_BATCH_DATA_UPDATE convert to integer"
        )


def get_solr_cohort_db_reload_data() -> str:
    return get_var("SOLR_COHORT_DB_RELOAD_DATA")
