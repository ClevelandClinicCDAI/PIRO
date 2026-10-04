import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def _setting(name, default=None, aliases=()):
    """Support Airflow Variables and local environment settings."""
    for key in (name, *aliases):
        value = os.getenv(f"AIRFLOW_VAR_{key}") or os.getenv(key)
        if value:
            return value
    # Import lazily: local catalog inspection does not require Airflow.
    try:
        from airflow.sdk import Variable
    except ImportError:
        value = default
    else:
        value = Variable.get(name, default=default)
    if value is None or value == "":
        raise ValueError(f"Missing configuration: {name}")
    return value


def get_concentriq_db_engine():
    server = _setting("CONCENTRIQ_DB_SERVER", aliases=("POSTGRES_SERVER",))
    embedded_port = None
    if "," in server:
        server, embedded_port = server.rsplit(",", 1)
    port = int(_setting(
        "CONCENTRIQ_DB_PORT", embedded_port or "5432",
        aliases=("POSTGRES_PORT",),
    ))
    url = URL.create(
        "postgresql+psycopg2",
        username=_setting("CONCENTRIQ_DB_USER", aliases=("POSTGRES_USER",)),
        password=_setting("CONCENTRIQ_DB_PASSWORD", aliases=("POSTGRES_PASSWORD",)),
        host=server.strip(),
        port=port,
        database=_setting(
            "CONCENTRIQ_DB_NAME", aliases=("POSTGRES_DATABASE", "POSTGRES_DB"),
        ),
    )
    return create_engine(
        url, pool_pre_ping=True, hide_parameters=True,
        connect_args={
            "connect_timeout": 10,
            "sslmode": _setting("CONCENTRIQ_DB_SSLMODE", "prefer"),
        },
    )


def get_concentriq_case_db_reload_data():
    return int(_setting("CONCENTRIQ_CASE_DB_RELOAD_DATA", "0"))


def get_concentriq_case_page_size():
    size = int(_setting("CONCENTRIQ_CASE_DETAIL_PAGE_SIZE", "1000"))
    if size <= 0:
        raise ValueError("CONCENTRIQ_CASE_DETAIL_PAGE_SIZE must be positive")
    return size
