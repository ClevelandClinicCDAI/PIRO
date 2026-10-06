"""Separate integration metadata and read projections of existing PIRO tables.

Only integration_metadata is deployed. Never create source_metadata in
production. Timestamps are naive America/New_York values. Security deadlines
and rate windows retain their UTC offsets to distinguish the repeated DST hour.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Unicode,
    UnicodeText,
    column,
)

integration_metadata: MetaData = MetaData()
clients: Table = Table(
    "ExternalApiClient",
    integration_metadata,
    Column("ClientId", String(32), primary_key=True),
    Column("Name", Unicode(100), nullable=False, unique=True),
    Column("IsActive", Boolean, nullable=False),
    Column("Scope", String(100), nullable=False),
    Column("CreatedAt", DateTime, nullable=False),
    Column("CreatedBy", Unicode(100), nullable=False),
)
keys: Table = Table(
    "ExternalApiKey",
    integration_metadata,
    Column("KeyId", String(32), primary_key=True),
    Column(
        "ClientId", String(32), ForeignKey(clients.c.ClientId), nullable=False
    ),
    Column("SecretHash", String(64), nullable=False),
    Column("CreatedAt", DateTime, nullable=False),
    Column("ExpiresAt", DateTime, nullable=False),
    Column("ExpiresAtOffsetMinutes", Integer, nullable=False),
    CheckConstraint(column("ExpiresAtOffsetMinutes").in_((-300, -240))),
    Column("RevokedAt", DateTime),
    Column("CreatedBy", Unicode(100), nullable=False),
    Index("IX_ExternalApiKey_ClientId", "ClientId"),
)
usage: Table = Table(
    "ExternalApiUsage",
    integration_metadata,
    Column(
        "ClientId",
        String(32),
        ForeignKey(clients.c.ClientId),
        primary_key=True,
    ),
    Column("QuotaDay", Date, nullable=False),
    Column("ReturnedRecords", Integer, nullable=False),
    Column("Minute", DateTime, nullable=False),
    Column("MinuteOffsetMinutes", Integer, nullable=False),
    CheckConstraint(column("MinuteOffsetMinutes").in_((-300, -240))),
    Column("RequestCount", Integer, nullable=False),
    CheckConstraint(column("ReturnedRecords") >= 0),
    CheckConstraint(column("RequestCount") >= 0),
)
leases: Table = Table(
    "ExternalApiLease",
    integration_metadata,
    Column("RequestId", String(32), primary_key=True),
    Column(
        "ClientId", String(32), ForeignKey(clients.c.ClientId), nullable=False
    ),
    Column("ExpiresAt", DateTime, nullable=False),
    Column("ExpiresAtOffsetMinutes", Integer, nullable=False),
    CheckConstraint(column("ExpiresAtOffsetMinutes").in_((-300, -240))),
    Index("IX_ExternalApiLease_ClientExpiry", "ClientId", "ExpiresAt"),
)
audits: Table = Table(
    "ExternalApiAudit",
    integration_metadata,
    Column("RequestId", String(32), primary_key=True),
    Column("ClientId", String(32)),
    Column("KeyId", String(32)),
    Column("Event", String(32), nullable=False),
    Column("Method", String(10)),
    Column("Route", String(200)),
    Column("OccurredAt", DateTime, nullable=False),
    Column("Actor", Unicode(100)),
    Column("SourceAddress", String(100)),
    Column("CaseNumbersJson", UnicodeText),
    Column("TestType", Unicode(200)),
    Column("CaseResultsJson", UnicodeText),
    Column("RecordCount", Integer, nullable=False),
    Column("StatusCode", Integer, nullable=False),
    Column("ErrorCode", String(64)),
    Column("ElapsedMs", Integer, nullable=False),
    Index("IX_ExternalApiAudit_ClientTime", "ClientId", "OccurredAt"),
)

source_metadata: MetaData = MetaData()
cases: Table = Table(
    "Case",
    source_metadata,
    Column("CaseId", Integer, primary_key=True),
    Column("CaseNumber", String(100), nullable=False),
)
orders: Table = Table(
    "LinkedOrder",
    source_metadata,
    Column("LinkedOrderId", Integer),
    Column("CaseId", Integer),
    Column("ComponentName", String(1000)),
    Column("ComponentExternalName", String(1000)),
    Column("ProcedureDesc", String(1000)),
    Column("DefaultUnit", String(1000)),
    Column("OrdValue", String(1000)),
    Column("OrdNumValue", Numeric(38, 5)),
)
