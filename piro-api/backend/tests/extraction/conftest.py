"""Setup for SearchRequest Extraction tests.

These tests use isolated DB fixtures because they need to test database-related
functionality (transaction rollbacks, etc)."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import Column, MetaData, Table, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema, DropSchema

from db.base_class import Base
from db.models.Case import Case


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Override the legacy fuzzy.db recreation for this isolated suite."""


def extraction_metadata():
    metadata = MetaData()
    # Keep the Case columns used by ORM result joins, without requiring the
    # unrelated patient/hospital fixture trees. All extraction FKs and the
    # CaseComment -> Case/CommentType relationships remain enforced.
    Table(
        "Case",
        metadata,
        *(
            Column(
                column.name,
                column.type,
                primary_key=column.primary_key,
                nullable=column.nullable,
                default=column.default,
                server_default=column.server_default,
            )
            for column in Case.__table__.columns
        ),
    )
    for name in (
        "User",
        "CommentType",
        "CaseComment",
        "ExtractionSession",
        "ExtractionRun",
        "ExtractionQueue",
        "ExtractionResult",
        "V_CaseCommentText",
        "CaseCommentSynopticSpecimen",
    ):
        Base.metadata.tables[name].to_metadata(metadata)
    return metadata


BACKENDS = ["sqlite"]
if os.getenv("PIRO_EXTRACTION_TEST_POSTGRES") == "1":
    BACKENDS.append("postgresql")


@pytest.fixture(params=BACKENDS)
def extraction_engine(request):
    if request.param == "sqlite":
        engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            hide_parameters=True,
        )

        @event.listens_for(engine, "connect")
        def enforce_foreign_keys(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        extraction_metadata().create_all(engine)
        try:
            yield engine
        finally:
            engine.dispose()
        return

    configured = os.getenv("PIRO_EXTRACTION_TEST_POSTGRES_URL")
    url = (
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
            "Extraction integration tests require localhost PostgreSQL."
        )
    base_engine = create_engine(url, hide_parameters=True)
    schema = "piro_extraction_test_" + uuid4().hex
    engine = base_engine.execution_options(schema_translate_map={None: schema})
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    try:
        extraction_metadata().create_all(engine)
        yield engine
    finally:
        # The only dropped objects belong to this generated fixture schema.
        with base_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        base_engine.dispose()


@pytest.fixture
def db(extraction_engine):
    # Match the production session's expiration and explicit-flush behavior.
    with sessionmaker(bind=extraction_engine, autoflush=False)() as session:
        yield session
