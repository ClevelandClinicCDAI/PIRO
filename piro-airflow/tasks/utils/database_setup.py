from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from tasks.utils.variable_setup import get_var
from tasks.utils.logging_setup import get_logger

logger = get_logger()


def get_piro_db_engine() -> Engine:
    """Create a sqlalchemy 'Engine' object for connecting to the PIRO DB.

    Also tests the connection after creation."""

    server, instance, db_name, username, password = (
        get_piro_db_connection_params()
    )  # noqa: E501

    piro_db_url = (
        f"mssql+pymssql://{username}:{password}@{server}\\{instance}/{db_name}"
    )
    engine = create_engine(piro_db_url)

    # test the connection
    with engine.connect() as con:
        con.execute("SELECT 1")
    logger.info(f"Can connect to the {db_name} database ({server}\\{instance})")

    return engine


def get_piro_db_connection_params() -> tuple[str, str, str, str, str]:
    """Construct a URL string using Airflow/Env variables for connecting to the PIRO DB."""  # noqa: E501
    server = get_var("PIRO_DB_SERVER")
    instance = get_var("PIRO_DB_INSTANCE")
    db_name = get_var("PIRO_DB_NAME")
    username = get_var("PIRO_DB_USERNAME")
    password = get_var("PIRO_DB_PASSWORD")

    return server, instance, db_name, username, password


def get_piro_db_session(engine: Engine = None) -> Session:
    """Create a SQLAlchemy 'scoped session' object for use in queries."""

    if not engine:
        engine = get_piro_db_engine()
    return Session(bind=engine)
