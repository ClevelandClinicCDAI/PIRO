"""ORM models for use with the external API.

We make a distinction between models used directly with the external API
(integration models) and read-only source models.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class IntegrationBase(DeclarativeBase):
    pass


class SourceBase(DeclarativeBase):
    pass


integration_metadata: MetaData = IntegrationBase.metadata
source_metadata: MetaData = SourceBase.metadata


class ExternalApiClient(IntegrationBase):
    __tablename__ = "ExternalApiClient"

    ClientId: Mapped[str] = mapped_column(String(32), primary_key=True)
    Name: Mapped[str] = mapped_column(
        Unicode(100), nullable=False, unique=True
    )
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False)
    Scope: Mapped[str] = mapped_column(String(100), nullable=False)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[str] = mapped_column(Unicode(100), nullable=False)


class ExternalApiKey(IntegrationBase):
    __tablename__ = "ExternalApiKey"

    KeyId: Mapped[str] = mapped_column(String(32), primary_key=True)
    ClientId: Mapped[str] = mapped_column(
        String(32), ForeignKey("ExternalApiClient.ClientId"), nullable=False
    )
    SecretHash: Mapped[str] = mapped_column(String(64), nullable=False)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ExpiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ExpiresAtOffsetMinutes: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    RevokedAt: Mapped[datetime | None] = mapped_column(DateTime)
    CreatedBy: Mapped[str] = mapped_column(Unicode(100), nullable=False)

    __table_args__ = (
        CheckConstraint(ExpiresAtOffsetMinutes.in_((-300, -240))),
        Index("IX_ExternalApiKey_ClientId", "ClientId"),
    )


class ExternalApiUsage(IntegrationBase):
    __tablename__ = "ExternalApiUsage"

    ClientId: Mapped[str] = mapped_column(
        String(32), ForeignKey("ExternalApiClient.ClientId"), primary_key=True
    )
    QuotaDay: Mapped[date] = mapped_column(Date, nullable=False)
    ReturnedRecords: Mapped[int] = mapped_column(Integer, nullable=False)
    Minute: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    MinuteOffsetMinutes: Mapped[int] = mapped_column(Integer, nullable=False)
    RequestCount: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(MinuteOffsetMinutes.in_((-300, -240))),
        CheckConstraint(ReturnedRecords >= 0),
        CheckConstraint(RequestCount >= 0),
    )


class ExternalApiLease(IntegrationBase):
    __tablename__ = "ExternalApiLease"

    RequestId: Mapped[str] = mapped_column(String(32), primary_key=True)
    ClientId: Mapped[str] = mapped_column(
        String(32), ForeignKey("ExternalApiClient.ClientId"), nullable=False
    )
    ExpiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ExpiresAtOffsetMinutes: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    __table_args__ = (
        CheckConstraint(ExpiresAtOffsetMinutes.in_((-300, -240))),
        Index("IX_ExternalApiLease_ClientExpiry", "ClientId", "ExpiresAt"),
    )


class ExternalApiAudit(IntegrationBase):
    __tablename__ = "ExternalApiAudit"

    RequestId: Mapped[str] = mapped_column(String(32), primary_key=True)
    ClientId: Mapped[str | None] = mapped_column(String(32))
    KeyId: Mapped[str | None] = mapped_column(String(32))
    Event: Mapped[str] = mapped_column(String(32), nullable=False)
    Method: Mapped[str | None] = mapped_column(String(10))
    Route: Mapped[str | None] = mapped_column(String(200))
    OccurredAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    Actor: Mapped[str | None] = mapped_column(Unicode(100))
    SourceAddress: Mapped[str | None] = mapped_column(String(100))
    CaseNumbersJson: Mapped[str | None] = mapped_column(UnicodeText)
    TestType: Mapped[str | None] = mapped_column(Unicode(200))
    CaseResultsJson: Mapped[str | None] = mapped_column(UnicodeText)
    RecordCount: Mapped[int] = mapped_column(Integer, nullable=False)
    StatusCode: Mapped[int] = mapped_column(Integer, nullable=False)
    ErrorCode: Mapped[str | None] = mapped_column(String(64))
    ElapsedMs: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("IX_ExternalApiAudit_ClientTime", "ClientId", "OccurredAt"),
    )


class Case(SourceBase):
    __tablename__ = "Case"

    CaseId: Mapped[int] = mapped_column(Integer, primary_key=True)
    CaseNumber: Mapped[str] = mapped_column(String(100), nullable=False)


class LinkedOrder(SourceBase):
    """Read projection with mapper identity, without adding a database key."""

    __tablename__ = "LinkedOrder"

    LinkedOrderId: Mapped[int] = mapped_column(Integer, nullable=True)
    CaseId: Mapped[int | None] = mapped_column(Integer)
    ComponentName: Mapped[str | None] = mapped_column(String(1000))
    ComponentExternalName: Mapped[str | None] = mapped_column(String(1000))
    ProcedureDesc: Mapped[str | None] = mapped_column(String(1000))
    DefaultUnit: Mapped[str | None] = mapped_column(String(1000))
    OrdValue: Mapped[str | None] = mapped_column(String(1000))
    OrdNumValue: Mapped[Decimal | None] = mapped_column(Numeric(38, 5))

    __mapper_args__ = {"primary_key": [LinkedOrderId]}
