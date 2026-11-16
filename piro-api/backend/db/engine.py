"""
Shared engine construction for PIRO's UI and external api.
"""

from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine, make_url


def create_database_engine(
    database_url: str | URL | None = None,
    *,
    echo: bool = False,
    query_timeout_seconds: int | None = None,
) -> Engine:
    """Create an Engine.

    Optional arguments can be provided that will limit query time. This feature
    is used by the external API.
    """
    if database_url is None:
        from db.session import SQLALCHEMY_DATABASE_URL

        database_url = SQLALCHEMY_DATABASE_URL
    url: URL = make_url(database_url)
    dialect: str = url.get_backend_name()
    options: dict[str, Any] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "echo": echo,
        "hide_parameters": True,
    }
    if dialect == "sqlite":
        options["connect_args"] = {"check_same_thread": False}
    elif query_timeout_seconds is not None:
        if dialect not in {"mssql", "postgresql"}:
            raise ValueError(
                "Unsupported database used with 'query_timeout_seconds' argument."  # noqa:E501
            )
        options.update(pool_size=5, max_overflow=5, pool_timeout=10)
        if dialect == "postgresql":
            # A startup option survives transaction rollbacks and applies to
            # every connection in this pool without affecting other pools.
            options["connect_args"] = {
                "options": f"-c statement_timeout={query_timeout_seconds * 1000}"  # noqa:E501
            }
        elif url.get_driver_name() != "pyodbc":
            raise ValueError("Bounded SQL Server queries require pyodbc.")

    engine: Engine = create_engine(url, **options)
    if dialect == "mssql" and query_timeout_seconds is not None:

        @event.listens_for(engine, "connect")
        def set_timeout(dbapi_connection: Any, _record: Any) -> None:
            """Set the ODBC statement timeout on this pool's connections."""
            dbapi_connection.timeout = query_timeout_seconds

    return engine
