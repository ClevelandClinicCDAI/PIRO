"""Naive Eastern storage with unambiguous expiry and elapsed-time arithmetic."""

from datetime import date, datetime, time, timedelta, timezone
from math import ceil
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.engine import Connection

EASTERN: ZoneInfo = ZoneInfo("America/New_York")


def database_now(connection: Connection) -> datetime:
    """Read an aware instant from the database clock shared by all workers."""
    if connection.dialect.name == "mssql":
        value: datetime = connection.scalar(select(func.sysutcdatetime()))
        return value.replace(tzinfo=timezone.utc)
    if connection.dialect.name == "postgresql":
        # CURRENT_TIMESTAMP is frozen at transaction start, possibly before
        # waiting for the client lock. Read the actual clock after that wait.
        return connection.scalar(select(func.clock_timestamp())).astimezone(
            timezone.utc
        )
    return datetime.now(timezone.utc)


def eastern_naive(instant: datetime) -> datetime:
    """Convert an aware instant to PIRO's naive Eastern storage convention."""
    if instant.tzinfo is None:
        raise ValueError("An aware instant is required.")
    return instant.astimezone(EASTERN).replace(tzinfo=None)


def eastern_offset(instant: datetime) -> int:
    """Return the Eastern UTC offset in minutes for a deadline or window."""
    if instant.tzinfo is None:
        raise ValueError("An aware instant is required.")
    offset: timedelta | None = instant.astimezone(EASTERN).utcoffset()
    assert offset is not None
    return int(offset.total_seconds() // 60)


def restore_instant(local: datetime, offset_minutes: int) -> datetime:
    """Disambiguate stored Eastern time, including the repeated fall hour."""
    if local.tzinfo is not None or offset_minutes not in {-300, -240}:
        raise ValueError("Invalid naive Eastern timestamp or offset.")
    return local.replace(
        tzinfo=timezone(timedelta(minutes=offset_minutes))
    ).astimezone(timezone.utc)


def eastern_day(instant: datetime) -> date:
    """Return the Eastern calendar date used for returned-record quotas."""
    return eastern_naive(instant).date()


def seconds_until_reset(instant: datetime) -> int:
    """Count real seconds to Eastern midnight, allowing 23- and 25-hour days."""
    tomorrow: date = eastern_day(instant) + timedelta(days=1)
    midnight: datetime = datetime.combine(tomorrow, time(), tzinfo=EASTERN)
    return max(
        1,
        ceil(
            (
                midnight.astimezone(timezone.utc)
                - instant.astimezone(timezone.utc)
            ).total_seconds()
        ),
    )
