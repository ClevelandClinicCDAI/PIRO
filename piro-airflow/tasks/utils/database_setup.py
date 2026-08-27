import oracledb
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from tasks.utils.variable_setup import get_var
from tasks.utils.logging_setup import get_logger

logger = get_logger()


def get_piro_db_connection_params() -> tuple[str, str, str, str, str]:
    """Construct a URL string using Airflow/Env variables for connecting to the PIRO DB."""  # noqa: E501
    server = get_var("PIRO_DB_SERVER")
    instance = get_var("PIRO_DB_INSTANCE")
    db_name = get_var("PIRO_DB_NAME")
    username = get_var("PIRO_DB_USERNAME")
    password = get_var("PIRO_DB_PASSWORD")

    return server, instance, db_name, username, password


def get_piro_db_engine() -> Engine:
    """Create a sqlalchemy 'Engine' object for connecting to the PIRO DB.

    Also tests the connection after creation."""

    server, instance, db_name, username, password = (
        get_piro_db_connection_params()
    )

    piro_db_url = (
        f"mssql+pymssql://{username}:{password}@{server}\\{instance}/{db_name}"
    )
    engine = create_engine(piro_db_url)

    # test the connection
    with engine.connect() as con:
        con.execute(text("SELECT 1"))
    logger.info(
        f"Can connect to the {db_name} database ({server}\\{instance})"
    )

    return engine


def get_piro_db_session(engine: Engine | None = None) -> Session:
    """Create a SQLAlchemy 'scoped session' object for use in queries."""

    if not engine:
        engine = get_piro_db_engine()
    return Session(bind=engine)


def get_clarity_db_connection_params() -> tuple[str, str, str, int, str]:
    """Construct a dictionary of connection parameters for connecting to
    Clarity."""

    user: str = get_var("CLARITY_DB_USER")
    password: str = get_var("CLARITY_DB_PASSWORD")
    host: str = get_var("CLARITY_DB_HOST")
    port_value: str = get_var("CLARITY_DB_PORT")
    port: int = int(port_value)
    service_name: str = get_var("CLARITY_DB_SERVICE_NAME")

    return user, password, host, port, service_name


def get_clarity_db_connection(
    test_connection: bool = False,
) -> oracledb.Connection:
    """Create an 'oracledb Connection for connecting to Clarity."""

    user, password, host, port, service_name = (
        get_clarity_db_connection_params()
    )

    dsn_string: str = f"{host}:{port}/{service_name}"

    connection: oracledb.Connection = oracledb.connect(
        user=user, password=password, dsn=dsn_string
    )

    if test_connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM dual")
            result = cursor.fetchone()
            if result is None or result[0] != 1:
                raise Exception("Failed to connect to Clarity database")
            else:
                logger.info("Successfully connected to Clarity database")

    return connection


def get_clarity_db_session(engine: Engine) -> Session:
    """Returns a SQLModel Session object for connecting to Clarity."""

    return Session(bind=engine)
