from tasks.utils.logging_setup import get_logger
from tasks.utils.variable_setup import get_var

logger = get_logger()


def get_concentriq_header_auth() -> str:
    return get_var("CONCENTRIQ_HEADER_AUTH")


def get_concentriq_case_details_import_url() -> str:
    return get_var("CONCENTRIQ_CASE_DETAIL_URL_DATA_IMPORT")


def get_concentriq_case_db_reload_data() -> int | None:
    try:
        return int(get_var("CONCENTRIQ_CASE_DB_RELOAD_DATA"))
    except (TypeError, ValueError):
        error_message: str = (
            "Invalid input: CONCENTRIQ_CASE_DB_RELOAD_DATA cannot be converted to integer"  # noqa:E501
        )
        logger.info(error_message)
        raise ValueError(error_message)


def get_concentriq_case_page_size() -> int | None:
    try:
        return int(get_var("CONCENTRIQ_CASE_DETAIL_PAGE_SIZE"))
    except (TypeError, ValueError):
        error_message: str = (
            "Invalid input: CONCENTRIQ_CASE_DETAIL_PAGE_SIZE cannot be converted to integer"  # noqa:E501
        )
        logger.info(error_message)
        raise ValueError(error_message)
