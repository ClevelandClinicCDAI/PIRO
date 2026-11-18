from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, Field, validator


class WorkLocationLoginEventCreate(BaseModel):
    """Inbound payload for a physician login signal.

    Mirrors prototypes/physician-location/app.py's LoginEvent so existing
    client scripts (e.g. send-production-login.ps1) need no payload changes
    to move from the prototype to this production endpoint.
    """

    class Config:
        extra = "forbid"

    event_id: str = Field(min_length=36, max_length=36)
    physician_id: str
    username: str
    device_id: str
    occurred_at: datetime
    event_type: Literal["logon"] = "logon"
    session_type: Literal["console", "remote"] = "console"
    network_context: Literal["onsite", "offsite", "unknown"] = "unknown"
    synthetic: Literal[False] = False

    @validator("occurred_at")
    def valid_time(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timezone is required")
        if value > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("Event timestamp is in the future")
        return value.astimezone(timezone.utc)

    def canonical_json(self) -> str:
        return json.dumps(
            json.loads(self.json()), sort_keys=True
        )


class WorkLocationLoginEventVM(BaseModel):
    EventId: str
    PhysicianId: str
    Username: str
    DeviceId: str
    EventType: str
    SessionType: str
    NetworkContext: str
    OccurredAt: datetime
    ReceivedAt: datetime

    class Config:
        orm_mode = True


class WorkLocationIngestResult(BaseModel):
    accepted: bool
    duplicate: bool
    event_id: str
