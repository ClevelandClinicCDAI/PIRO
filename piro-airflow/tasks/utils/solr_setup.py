from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var

logger = get_logger()


def get_solr_header_auth() -> str:
    return get_var("SOLR_HEADER_AUTH")


def get_solr_case_data_import_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_IMPORT")


def get_solr_case_data_update_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_UPDATE")


def get_solr_case_update_batch_size() -> int:
    try:
        return int(get_var("SOLR_CASE_UPDATE_BATCH_SIZE"))
    except (TypeError, ValueError):
        logger.error(
            "Invalid input: SOLR_CASE_UPDATE_BATCH_SIZE cannot be converted to integer; defaulting to 1000"  # noqa:E501
        )
        return 1000


def get_solr_case_status_url() -> str:
    return get_var("SOLR_CASE_URL_STATUS")


def get_solr_case_data_count_url() -> str:
    return get_var("SOLR_CASE_URL_DATA_COUNT")


def get_solr_case_suggest_data_import_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_IMPORT")


def get_solr_case_suggest_data_update_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_UPDATE")


def get_solr_case_suggest_data_update_batch() -> int:
    try:
        return int(get_var("SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE"))
    except (TypeError, ValueError):
        error_message: str = (
            "Invalid input: SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE cannot be converted to integer"  # noqa:E501
        )
        logger.error(error_message)
        raise ValueError(error_message)


def get_solr_case_suggest_status_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_STATUS")


def get_solr_case_suggest_data_count_url() -> str:
    return get_var("SOLR_CASE_SUGGEST_URL_DATA_COUNT")


def get_solr_case_staff_data_import_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_DATA_IMPORT")


def get_solr_case_staff_data_update_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_DATA_UPDATE")


def get_solr_case_staff_data_update_batch() -> int:
    try:
        return int(get_var("SOLR_CASE_STAFF_BATCH_DATA_UPDATE"))
    except (TypeError, ValueError):
        error_message: str = (
            "Invalid input: SOLR_CASE_STAFF_BATCH_DATA_UPDATE cannot be converted to integer"  # noqa:E501
        )
        logger.error(error_message)
        raise ValueError(error_message)


def get_solr_case_staff_status_url() -> str:
    return get_var("SOLR_CASE_STAFF_URL_STATUS")


def get_solr_cohort_data_update_url() -> str:
    return get_var("SOLR_COHORT_URL_DATA_UPDATE")


def get_solr_cohort_data_import_url() -> str:
    return get_var("SOLR_COHORT_URL_DATA_IMPORT")


def get_solr_cohort_status_url() -> str:
    return get_var("SOLR_COHORT_URL_STATUS")


def get_solr_cohort_data_update_batch() -> int:
    try:
        return int(get_var("SOLR_COHORT_BATCH_DATA_UPDATE"))
    except (TypeError, ValueError):
        error_message: str = (
            "Invalid input: SOLR_COHORT_BATCH_DATA_UPDATE cannot be converted to integer"  # noqa:E501
        )
        logger.info(error_message)
        raise ValueError(error_message)
