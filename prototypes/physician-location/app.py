"""Isolated simulated-presence API. Never imports PIRO's shared DB session."""
import hmac
import json
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, validator

DB_PATH = os.environ.get("PRESENCE_DB_PATH", "/data/presence.sqlite3")
LOCAL_TZ = ZoneInfo("America/New_York")
NAMES = ["Emily Chen", "Michael Torres", "Sarah Patel", "David Kim", "Jessica Morgan",
         "Matthew Lewis", "Ashley Rivera", "Robert Nguyen", "Lauren Mitchell", "Daniel Brooks",
         "Priya Desai", "Kevin Zhao", "Natalie Sanders", "Andrew Wilson", "Katherine Lee",
         "Steven Martin", "Rachel Adams", "Thomas Clark", "Megan Scott", "Jason Hall",
         "Amanda Price", "Brian Carter", "Stephanie Young", "Ryan Cooper", "Allison Green"]
SPECIALTIES = ["Gastrointestinal Pathology", "Cytopathology", "Breast Pathology", "Hematopathology",
               "Dermatopathology", "Genitourinary Pathology", "Neuropathology", "Thoracic Pathology",
               "Pediatric Pathology", "Soft Tissue and Bone Pathology", "Molecular Genetic Pathology",
               "Head and Neck Pathology", "Transfusion Medicine"]
REGIONS = ["Akron", "NE Ohio", "Weston", "Mercy", "Indian River", "Ohio (other)"]
PHYSICIANS = [{"physician_id": f"synthetic-{i+1:03}", "name": name + ", MD",
               "username": "DEMO\\" + name.lower().replace(" ", "."),
               "subspecialty": SPECIALTIES[i % len(SPECIALTIES)],
               "region": REGIONS[i % len(REGIONS)]} for i, name in enumerate(NAMES)]
ROSTER_METADATA = {"source": "Fictional demo roster", "real_names": False}
roster_path = Path(os.environ.get("PRESENCE_ROSTER_PATH", str(Path(__file__).with_name("roster.local.json"))))
if roster_path.exists():
    snapshot = json.loads(roster_path.read_text())
    PHYSICIANS = snapshot["physicians"]
    ROSTER_METADATA = {key: value for key, value in snapshot.items() if key != "physicians"}
ROSTER = {p["physician_id"]: p for p in PHYSICIANS}
# Distinct Building values from computer_list.xlsx, Onsite!E2:E151.
DEVICES = json.loads(Path(__file__).with_name("buildings.json").read_text())


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app):
    if os.environ.get("PRESENCE_PROTOTYPE_ENABLED") != "true" or not os.environ.get("PRESENCE_INGEST_TOKEN"):
        raise RuntimeError("Explicit prototype enablement and an ingestion token are required")
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS login_events (
            event_id TEXT PRIMARY KEY, physician_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL, received_at TEXT NOT NULL,
            payload TEXT NOT NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS event_time ON login_events(occurred_at)")
    yield


app = FastAPI(title="PIRO synthetic physician-location prototype", lifespan=lifespan)


class LoginEvent(BaseModel):
    class Config:
        extra = "forbid"
    event_id: UUID
    physician_id: str
    username: str
    device_id: str = Field(pattern=r"^DEMO-[A-Z0-9-]{1,50}$")
    occurred_at: datetime
    event_type: Literal["logon"] = "logon"
    session_type: Literal["console", "remote"] = "console"
    network_context: Literal["onsite", "offsite", "unknown"] = "unknown"
    synthetic: Literal[True]

    @validator("occurred_at")
    def valid_time(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timezone is required")
        if value > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("Event timestamp is in the future")
        return value.astimezone(timezone.utc)


def authorize(x_presence_token: str = Header(default="")):
    expected = os.environ.get("PRESENCE_INGEST_TOKEN", "")
    if not expected or not hmac.compare_digest(x_presence_token, expected):
        raise HTTPException(401, "Valid prototype ingestion credential required")


def classify(event):
    if event["session_type"] == "remote":
        return "Unknown", "Remote session — physical location unknown"
    if event["network_context"] == "offsite":
        return "Remote", "Off-site (synthetic signal)"
    site = DEVICES.get(event["device_id"])
    if event["network_context"] == "onsite" and site:
        return "In Office", site
    return "Unknown", "Insufficient location evidence"


@app.post("/work-location/events", dependencies=[Depends(authorize)])
def ingest(event: LoginEvent):
    person = ROSTER.get(event.physician_id)
    if not person or person["username"] != event.username:
        raise HTTPException(422, "Use a demo identity from the prototype roster")
    payload = json.loads(event.json())
    canonical = json.dumps(payload, sort_keys=True)
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute("SELECT payload FROM login_events WHERE event_id=?", (str(event.event_id),)).fetchone()
        if existing:
            if existing["payload"] != canonical:
                raise HTTPException(409, "Event ID already belongs to a different event")
            return {"accepted": True, "duplicate": True, "event_id": str(event.event_id)}
        conn.execute("INSERT INTO login_events VALUES (?, ?, ?, ?, ?)",
                     (str(event.event_id), event.physician_id, event.occurred_at.isoformat(),
                      datetime.now(timezone.utc).isoformat(), canonical))
    return {"accepted": True, "duplicate": False, "event_id": str(event.event_id)}


@app.get("/work-location/physicians")
def physicians(day: date | None = None):
    selected = day or datetime.now(LOCAL_TZ).date()
    start = datetime.combine(selected, datetime.min.time(), LOCAL_TZ)
    end = datetime.combine(selected + timedelta(days=1), datetime.min.time(), LOCAL_TZ)
    with connect() as conn:
        rows = conn.execute("""SELECT * FROM login_events WHERE occurred_at >= ? AND occurred_at < ?
                               ORDER BY occurred_at DESC, received_at DESC, event_id DESC""",
                            (start.astimezone(timezone.utc).isoformat(), end.astimezone(timezone.utc).isoformat())).fetchall()
    grouped = {}
    for row in rows:
        event = json.loads(row["payload"])
        event["received_at"] = row["received_at"]
        event["status"], event["site"] = classify(event)
        grouped.setdefault(row["physician_id"], []).append(event)
    result = []
    for person in PHYSICIANS:
        events = grouped.get(person["physician_id"], [])
        last = events[0] if events else None
        result.append({**person, "events": events, "status": last["status"] if last else "No Activity Today",
                       "site": last["site"] if last else "—", "last_observed": last["occurred_at"] if last else None})
    return {"synthetic": True, "simulated_locations": True, "roster": ROSTER_METADATA,
            "day": str(selected), "timezone": "America/New_York", "physicians": result}
