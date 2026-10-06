"""Exercise shared connection construction and PostgreSQL-specific behavior."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from apis.external_api.models import cases, orders
from apis.external_api.timeutil import database_now
from db.engine import create_database_engine
from sqlalchemy import insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError

from tests.external_api.types import ApiFixture


def test_postgres_preserves_full_source_decimal_precision(
    api: ApiFixture,
) -> None:
    """Return all 38 decimal digits without a binary floating-point conversion."""
    value: str = "9" * 33 + ".12345"
    with api["engine"].begin() as connection:
        connection.execute(
            insert(cases).values(CaseId=1, CaseNumber="PRECISION")
        )
        connection.execute(
            insert(orders).values(
                LinkedOrderId=1, CaseId=1, OrdNumValue=Decimal(value)
            )
        )
    response = api["client"].post(
        "/linked-orders/search",
        json={"case_numbers": ["PRECISION"]},
        headers=api["headers"],
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["OrdNumValue"] == value


def test_postgres_timeout_is_pool_local_and_survives_rollback(
    postgres_engine: Engine,
) -> None:
    """Bound external queries without altering the existing UI pool settings."""
    normal: Engine = create_database_engine(postgres_engine.url)
    bounded: Engine = create_database_engine(
        postgres_engine.url, query_timeout_seconds=1
    )
    try:
        with normal.connect() as connection:
            original: str = connection.exec_driver_sql(
                "SHOW statement_timeout"
            ).scalar_one()
        with bounded.connect() as connection:
            assert (
                connection.exec_driver_sql(
                    "SHOW statement_timeout"
                ).scalar_one()
                == "1s"
            )
            with pytest.raises(DBAPIError):
                connection.exec_driver_sql("SELECT pg_sleep(2)")
            connection.rollback()
            assert (
                connection.exec_driver_sql(
                    "SHOW statement_timeout"
                ).scalar_one()
                == "1s"
            )
            assert connection.scalar(select(1)) == 1
        with normal.connect() as connection:
            assert (
                connection.exec_driver_sql(
                    "SHOW statement_timeout"
                ).scalar_one()
                == original
            )
    finally:
        normal.dispose()
        bounded.dispose()


def test_database_clock_is_an_aware_instant_independent_of_session_timezone(
    postgres_engine: Engine,
) -> None:
    """Use the database clock even when its session timezone differs from PIRO."""
    before: datetime = datetime.now(timezone.utc)
    with postgres_engine.begin() as connection:
        connection.exec_driver_sql("SET LOCAL TIME ZONE 'Asia/Tokyo'")
        instant: datetime = database_now(connection)
    assert instant.tzinfo is timezone.utc
    assert abs((instant - before).total_seconds()) < 10
