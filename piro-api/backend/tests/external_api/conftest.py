"""Run external API tests in disposable schemas on localhost PostgreSQL."""

import os
from collections.abc import Iterator
from uuid import uuid4

import pytest
from apis.external_api.admin import create_client, issue_key
from apis.external_api.app import create_external_app
from apis.external_api.config import ExternalAPISettings
from apis.external_api.models import integration_metadata, source_metadata
from db.engine import create_database_engine
from fastapi.testclient import TestClient
from sqlalchemy.engine import URL, Engine, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import CreateSchema, DropSchema

from tests.external_api.types import ApiFixture


@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> None:
    """Override the legacy SQLite bootstrap only for this PostgreSQL suite."""


@pytest.fixture(scope="session")
def postgres_engine() -> Iterator[Engine]:
    """Connect to the local test database without creating or dropping it."""
    configured: str | None = os.getenv("PIRO_EXTERNAL_TEST_POSTGRES_URL")
    url: URL = (
        make_url(configured)
        if configured
        else URL.create(
            "postgresql+psycopg2",
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "testdb"),
        )
    )
    if url.get_backend_name() != "postgresql" or url.host not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        pytest.fail(
            "External tests require a localhost PostgreSQL URL.", pytrace=False
        )
    engine: Engine = create_database_engine(url, query_timeout_seconds=30)
    try:
        try:
            with engine.connect():
                pass
        except SQLAlchemyError:
            pytest.fail(
                "Cannot connect to localhost PostgreSQL. Set PIRO_EXTERNAL_TEST_POSTGRES_URL "  # noqa:E501
                "or POSTGRES_* test settings; the role needs CREATE SCHEMA permission.",  # noqa:E501
                pytrace=False,
            )
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def api(postgres_engine: Engine) -> Iterator[ApiFixture]:
    """Create isolated source fixtures and integration tables for one test."""
    schema: str = "piro_external_test_" + uuid4().hex
    engine: Engine = postgres_engine.execution_options(
        schema_translate_map={None: schema}
    )
    with postgres_engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    try:
        integration_metadata.create_all(engine)
        source_metadata.create_all(engine)
        config: ExternalAPISettings = ExternalAPISettings(
            enabled=True, _env_file=None  # type: ignore[attr-defined]
        )
        client_id: str = create_client(engine, "Airflow test", "pytest")
        credential: dict[str, str] = issue_key(engine, client_id, "pytest")
        app = create_external_app(config, engine)
        with TestClient(app) as client:
            yield {
                "engine": engine,
                "config": config,
                "client_id": client_id,
                "credential": credential,
                "app": app,
                "client": client,
                "headers": {"X-API-Key": credential["api_key"]},
            }
    finally:
        # Drop only this generated test schema; never public or dbo objects.
        with postgres_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
