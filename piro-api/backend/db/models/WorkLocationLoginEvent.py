from db.base_class import Base
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func


class WorkLocationLoginEvent(Base):
    """A single physician login signal used to infer work location.

    EventId is the client-generated UUID (see prototype at
    prototypes/physician-location/app.py) and is the primary key, which
    makes re-submission of the same event idempotent: a repeat POST with
    the same EventId is treated as a duplicate rather than a new row.
    """

    __tablename__ = "WorkLocationLoginEvent"

    EventId = Column(String(36), primary_key=True, index=True)
    PhysicianId = Column(String(50), nullable=False, index=True)
    Username = Column(String(200), nullable=False)
    DeviceId = Column(String(100), nullable=False)
    EventType = Column(String(20), nullable=False, default="logon")
    SessionType = Column(String(20), nullable=False, default="console")
    NetworkContext = Column(String(20), nullable=False, default="unknown")
    OccurredAt = Column(DateTime(timezone=True), nullable=False, index=True)
    ReceivedAt = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Canonical JSON of the validated payload, used to detect whether a
    # repeated EventId represents the same event (duplicate, accepted) or a
    # conflicting one (rejected).
    Payload = Column(Text, nullable=False)
