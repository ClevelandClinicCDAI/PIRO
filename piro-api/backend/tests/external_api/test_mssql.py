"""Opt-in SQL Server checks in a disposable, uniquely named schema.

Set PIRO_EXTERNAL_TEST_DATABASE_URL to a NONPRODUCTION mssql+pyodbc URL.
Set PIRO_EXTERNAL_TEST_ALLOW_SCHEMA_CREATE=yes to acknowledge schema creation.
Only tables in the generated piro_external_test_<uuid> schema are touched.
"""

import os
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from apis.external_api.admin import create_client, issue_key
from apis.external_api.app import create_external_app
from apis.external_api.config import ExternalAPISettings
from apis.external_api.models import (
    audits,
    cases,
    integration_metadata,
    orders,
    source_metadata,
)
from db.engine import create_database_engine
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema, DropSchema


@pytest.fixture
def sql_api() -> Iterator[tuple[TestClient, Engine, dict[str, str]]]:
    """Deploy and clean up tables only in a generated SQL Server schema."""
    url = os.getenv("PIRO_EXTERNAL_TEST_DATABASE_URL")
    if not url or os.getenv("PIRO_EXTERNAL_TEST_ALLOW_SCHEMA_CREATE") != "yes":
        pytest.skip(
            "SQL Server integration database/schema permission not configured"
        )
    raw_engine = create_database_engine(url, query_timeout_seconds=30)
    assert (
        raw_engine.dialect.name == "mssql"
    ), "This fixture requires SQL Server."
    schema = "piro_external_test_" + uuid4().hex
    engine = raw_engine.execution_options(schema_translate_map={None: schema})
    with raw_engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    try:
        sql = (
            Path(__file__).resolve().parents[4]
            / "piro-sql"
            / "deploy_external_api.sql"
        ).read_text(encoding="utf-8-sig")
        sql = sql.replace("dbo.", schema + ".")
        with raw_engine.begin() as connection:
            connection.exec_driver_sql(sql)
            connection.exec_driver_sql(sql)  # Deployment must be repeatable.
        source_metadata.create_all(engine)
        with engine.begin() as connection:
            connection.execute(
                insert(cases),
                [
                    {"CaseId": 1, "CaseNumber": "SQL-1"},
                    {"CaseId": 2, "CaseNumber": "SQL-1"},
                ],
            )
            connection.execute(
                insert(orders),
                [
                    {
                        "LinkedOrderId": 1,
                        "CaseId": 1,
                        "ComponentName": "PD-L1 10% [x]_\\",
                        "OrdNumValue": Decimal("9" * 33 + ".12345"),
                    },
                    {
                        "LinkedOrderId": 2,
                        "CaseId": 2,
                        "ComponentName": "pd-l1 10% [x]_\\",
                        "OrdNumValue": Decimal("0.00001"),
                    },
                    {
                        "LinkedOrderId": 3,
                        "CaseId": 2,
                        "ComponentName": "unrelated",
                        "OrdNumValue": None,
                    },
                ],
            )
        client_id = create_client(engine, "SQL integration test", "pytest")
        key = issue_key(engine, client_id, "pytest")
        app = create_external_app(
            ExternalAPISettings(enabled=True, _env_file=None), engine
        )
        with TestClient(app) as client:
            yield client, engine, key
    finally:
        # The generated schema is the only cleanup target, never dbo.
        source_metadata.drop_all(engine)
        integration_metadata.drop_all(engine)
        with raw_engine.begin() as connection:
            connection.execute(DropSchema(schema))
        raw_engine.dispose()


def test_mssql_deployment_query_precision_and_audit(
    sql_api: tuple[TestClient, Engine, dict[str, str]],
) -> None:
    """Verify mssql deployment query precision and audit."""
    client, engine, key = sql_api
    response = client.post(
        "/linked-orders/search",
        headers={"X-API-Key": key["api_key"]},
        json={
            "case_numbers": ["SQL-1", "NOT-FOUND"],
            "test_type": "pd-l1 10% [x]_\\",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["record_count"] == 2
    assert response.json()["data"][0]["OrdNumValue"] == "9" * 33 + ".12345"
    assert response.json()["data"][1]["OrdNumValue"] == "0.00001"
    assert response.json()["cases"][1]["status"] == "case_not_found"
    with engine.connect() as connection:
        assert (
            connection.scalar(
                select(audits.c.RecordCount).where(
                    audits.c.RequestId == response.json()["request_id"],
                )
            )
            == 2
        )


def test_mssql_migrates_utc_history_and_deadlines_without_reinterpretation(
    sql_api: tuple[TestClient, Engine, dict[str, str]],
) -> None:
    """Convert the initial schema atomically and preserve both DST instants."""
    import re
    from datetime import datetime, timezone

    from apis.external_api.models import clients, keys, leases, usage
    from apis.external_api.timeutil import restore_instant

    _, engine, _ = sql_api
    schema: str = engine.get_execution_options()["schema_translate_map"][None]
    sql_root: Path = Path(__file__).resolve().parents[4] / "piro-sql"
    deployment: str = (sql_root / "deploy_external_api.sql").read_text(
        encoding="utf-8-sig"
    )
    # Reconstruct the pre-release table shape; no production table is touched.
    legacy: str = re.sub(
        r"-- Never silently reinterpret.*?END;\n",
        "",
        deployment,
        flags=re.DOTALL,
    )
    legacy = "\n".join(
        line for line in legacy.splitlines() if "OffsetMinutes" not in line
    )
    for current, old in [
        ("CreatedAt", "CreatedAtUtc"),
        ("ExpiresAt", "ExpiresAtUtc"),
        ("RevokedAt", "RevokedAtUtc"),
        ("Minute", "MinuteUtc"),
        ("OccurredAt", "OccurredAtUtc"),
    ]:
        legacy = legacy.replace(current, old)
    integration_metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(legacy.replace("dbo.", schema + "."))
        connection.exec_driver_sql(f"""
INSERT INTO {schema}.ExternalApiClient
    (ClientId, Name, IsActive, Scope, CreatedAtUtc, CreatedBy)
VALUES ('client', 'legacy', 1, 'linked-orders:read', '2026-11-01T05:30:00', 'pytest');
INSERT INTO {schema}.ExternalApiKey
    (KeyId, ClientId, SecretHash, CreatedAtUtc, ExpiresAtUtc, RevokedAtUtc, CreatedBy)
VALUES ('key', 'client', 'hash', '2026-11-01T05:30:00', '2026-11-01T06:30:00', NULL, 'pytest');
INSERT INTO {schema}.ExternalApiUsage
    (ClientId, QuotaDay, ReturnedRecords, MinuteUtc, RequestCount)
VALUES ('client', '2026-11-01', 12, '2026-11-01T06:30:00', 2);
INSERT INTO {schema}.ExternalApiLease (RequestId, ClientId, ExpiresAtUtc)
VALUES ('lease', 'client', '2026-11-01T05:30:00');
INSERT INTO {schema}.ExternalApiAudit
    (RequestId, Event, OccurredAtUtc, RecordCount, StatusCode, ElapsedMs)
VALUES ('audit', 'request', '2026-11-01T05:30:00', 12, 200, 1);
""")
    migration: str = (
        (sql_root / "migrate_external_api_eastern.sql")
        .read_text(encoding="utf-8-sig")
        .replace("dbo.", schema + ".")
    )
    with engine.begin() as connection:
        connection.exec_driver_sql(migration)
        connection.exec_driver_sql(migration)
        connection.exec_driver_sql(deployment.replace("dbo.", schema + "."))
        assert connection.scalar(select(clients.c.CreatedAt)) == datetime(
            2026, 11, 1, 1, 30
        )
        key = connection.execute(select(keys)).mappings().one()
        assert key.RevokedAt is None
        assert key.SecretHash == "hash"
        assert restore_instant(
            key.ExpiresAt, key.ExpiresAtOffsetMinutes
        ) == datetime(2026, 11, 1, 6, 30, tzinfo=timezone.utc)
        lease = connection.execute(select(leases)).mappings().one()
        assert restore_instant(
            lease.ExpiresAt, lease.ExpiresAtOffsetMinutes
        ) == datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc)
        state = connection.execute(select(usage)).mappings().one()
        assert state.Minute == datetime(2026, 11, 1, 1, 30)
        assert state.MinuteOffsetMinutes == -300
        assert state.ReturnedRecords == 12
        assert state.RequestCount == 2
        assert connection.scalar(select(audits.c.OccurredAt)) == datetime(
            2026, 11, 1, 1, 30
        )
