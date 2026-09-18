from typing import Generator
import warnings
import pysolr
from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = ""

if settings.DATABASE == "SQLITE":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    engine_inst = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True,
    )
elif settings.DATABASE == "MSSQL":
    if settings.MSSQL_WINDOW_AUTH == "True":
        SQLALCHEMY_DATABASE_URL = settings.MSSQL_DB_URL_WIN
    else:
        SQLALCHEMY_DATABASE_URL = settings.MSSQL_DB_URL_SQL
    # pool_pre_ping validates a pooled connection (cheap SELECT 1) before
    # handing it to a request, transparently reconnecting if the network/DB
    # has silently dropped it (e.g. firewall/idle timeout on the SQL Server
    # link). Without this, long-running requests (like LLM data extraction)
    # leave connections idle in the pool long enough to go stale, so the
    # next request to reuse one fails immediately with a pyodbc
    # OperationalError ("TCP Provider: Error code 0x2746 (10054)") before
    # any of its own logic runs. pool_recycle proactively retires
    # connections older than 280s so they're never given the chance to go
    # stale in the first place.
    engine_inst = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=280,
    )
elif settings.DATABASE == "POSTGRES":
    SQLALCHEMY_DATABASE_URL = settings.POSTGRES_DB_URL
    engine_inst = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
        pool_recycle=280,
    )
else:
    raise Exception("Settings DATABASE is not set in the env file")


# if you don't want to install postgres or any database, use sqlite, a file
# system based database,
# uncomment below lines if you would like to use sqlite and comment above 2
# lines of SQLALCHEMY_DATABASE_URL AND engine

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_inst
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        del db


def get_solr() -> Generator:
    try:
        warnings.filterwarnings("ignore")
        # Create a client instance. The timeout and authentication options are not required. # noqa
        solr = pysolr.Solr(
            f"{settings.SOLR_URL}/{settings.SOLR_CORE}/",
            auth=(settings.SOLR_USER_NAME, settings.SOLR_USER_PASSWORD),
            always_commit=False,
            timeout=10,
            verify=False,
        )
        # ,'http://localhost:8983/solr/PIROCase/'
        # Note that auto_commit defaults to False for performance. You can set
        # `auto_commit=True` to have commands always update the index immediately, make # noqa
        # an update call with `commit=True`, or use Solr's `autoCommit` / `commitWithin` # noqa
        # to have your data be committed following a particular policy.

        # Do a health check.
        # solr.ping()
        yield solr
    finally:
        del solr
