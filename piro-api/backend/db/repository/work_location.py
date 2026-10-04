from datetime import datetime, timezone

from db.models.WorkLocationLoginEvent import WorkLocationLoginEvent
from fastapi import HTTPException
from sqlalchemy.orm import Session
from viewmodel.workLocation import WorkLocationLoginEventCreate


def create_login_event(
    event: WorkLocationLoginEventCreate, db: Session
) -> tuple[WorkLocationLoginEvent, bool]:
    """Insert a login event, treating a repeated event_id as idempotent.

    Returns (row, duplicate). Raises HTTPException (409) if the same
    event_id was previously submitted with different contents.
    """
    canonical = event.canonical_json()

    existing = (
        db.query(WorkLocationLoginEvent)
        .filter(WorkLocationLoginEvent.EventId == event.event_id)
        .first()
    )
    if existing:
        if existing.Payload != canonical:
            raise HTTPException(
                status_code=409,
                detail="Event ID already belongs to a different event",
            )
        return existing, True

    row = WorkLocationLoginEvent(
        EventId=event.event_id,
        PhysicianId=event.physician_id,
        Username=event.username,
        DeviceId=event.device_id,
        EventType=event.event_type,
        SessionType=event.session_type,
        NetworkContext=event.network_context,
        OccurredAt=event.occurred_at,
        ReceivedAt=datetime.now(timezone.utc),
        Payload=canonical,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row, False
