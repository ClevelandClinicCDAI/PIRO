"""Verify naive Eastern storage preserves security across DST transitions."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from apis.external_api.admin import create_client, issue_key, revoke_key
from apis.external_api.errors import ExternalAPIError
from apis.external_api.models import audits, clients, keys, leases, usage
from apis.external_api.service import ExternalService
from apis.external_api.timeutil import (
    eastern_naive,
    eastern_offset,
    restore_instant,
)
from apis.external_api.v1.schemas import SearchResponse
from sqlalchemy import select

from tests.external_api.test_limits import context
from tests.external_api.types import ApiFixture


def set_clock(monkeypatch: pytest.MonkeyPatch, instant: datetime) -> None:
    """Use the same deterministic aware database clock in all API components."""
    for module in ("admin", "security", "service"):
        monkeypatch.setattr(
            f"apis.external_api.{module}.database_now",
            lambda _connection: instant,
        )


def test_administrative_timestamps_are_naive_eastern(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Store local timestamps while the CLI expiry retains an explicit offset."""
    now: datetime = datetime(2026, 10, 31, 6, 30, tzinfo=timezone.utc)
    set_clock(monkeypatch, now)
    client_id: str = create_client(api["engine"], "DST client", "pytest")
    credential: dict[str, str] = issue_key(
        api["engine"], client_id, "pytest", 1
    )
    revoke_key(api["engine"], credential["key_id"], "pytest")
    with api["engine"].connect() as connection:
        created: datetime = connection.scalar(
            select(clients.c.CreatedAt).where(clients.c.ClientId == client_id)
        )
        row = (
            connection.execute(
                select(keys).where(keys.c.KeyId == credential["key_id"])
            )
            .mappings()
            .one()
        )
        assert (
            created
            == row.CreatedAt
            == row.RevokedAt
            == datetime(2026, 10, 31, 2, 30)
        )
        assert created.tzinfo is None
        assert row.ExpiresAt == datetime(2026, 11, 1, 1, 30)
        assert row.ExpiresAtOffsetMinutes == -300
        assert credential["expires_at"] == "2026-11-01T01:30:00-05:00"
        times = connection.scalars(
            select(audits.c.OccurredAt).where(audits.c.ClientId == client_id)
        ).all()
        assert len(times) == 3
        assert all(
            value == created and value.tzinfo is None for value in times
        )


@pytest.mark.parametrize("hour,offset", [(5, -240), (6, -300)])
def test_key_expiry_is_unambiguous_through_repeated_hour(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch, hour: int, offset: int
) -> None:
    """An expired key cannot revive, and a second-fold key cannot expire early."""
    issued: datetime = datetime(2026, 10, 31, hour, 30, tzinfo=timezone.utc)
    expiry: datetime = issued + timedelta(days=1)
    set_clock(monkeypatch, issued)
    credential: dict[str, str] = issue_key(
        api["engine"], api["client_id"], "pytest", 1
    )
    service: ExternalService = api["app"].state.service
    with api["engine"].connect() as connection:
        assert (
            connection.scalar(
                select(keys.c.ExpiresAtOffsetMinutes).where(
                    keys.c.KeyId == credential["key_id"]
                )
            )
            == offset
        )
    set_clock(monkeypatch, expiry - timedelta(minutes=45))
    principal = service.authenticate(credential["api_key"])
    set_clock(monkeypatch, expiry)
    with pytest.raises(ExternalAPIError, match="invalid_api_key"):
        service.authenticate(credential["api_key"])
    set_clock(monkeypatch, expiry + timedelta(minutes=45))
    with pytest.raises(ExternalAPIError, match="invalid_api_key"):
        service.authenticate(credential["api_key"])
    with pytest.raises(ExternalAPIError, match="invalid_api_key"):
        service.admit(principal, uuid4().hex)


@pytest.mark.parametrize(
    "start",
    [
        datetime(2026, 3, 8, 6, 59, 30, tzinfo=timezone.utc),
        datetime(2026, 11, 1, 5, 59, 30, tzinfo=timezone.utc),
    ],
)
def test_lease_duration_survives_both_dst_transitions(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch, start: datetime
) -> None:
    """Retain slots for real elapsed time and reject expired worker results."""
    service: ExternalService = api["app"].state.service
    principal = service.authenticate(api["credential"]["api_key"])
    api["config"].max_concurrent = 1
    set_clock(monkeypatch, start)
    old = context(principal)
    service.admit(principal, old["request_id"])
    with api["engine"].connect() as connection:
        lease = connection.execute(select(leases)).mappings().one()
        assert lease.ExpiresAt.tzinfo is None
        assert restore_instant(
            lease.ExpiresAt, lease.ExpiresAtOffsetMinutes
        ) == start + timedelta(seconds=120)
    set_clock(monkeypatch, start + timedelta(seconds=60))
    with pytest.raises(ExternalAPIError, match="concurrency_limit_exceeded"):
        service.admit(principal, uuid4().hex)
    set_clock(monkeypatch, start + timedelta(seconds=121))
    service.admit(principal, uuid4().hex)
    with pytest.raises(ExternalAPIError, match="request_lease_expired"):
        service.complete(
            old,
            SearchResponse(
                request_id=old["request_id"], data=[], cases=[], record_count=0
            ),
        )


def test_repeated_minutes_have_distinct_rate_windows(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Treat each occurrence of 01:30 as its own bounded fixed minute."""
    service: ExternalService = api["app"].state.service
    principal = service.authenticate(api["credential"]["api_key"])
    api["config"].requests_per_minute = 1
    for hour, offset in [(5, -240), (6, -300)]:
        set_clock(
            monkeypatch,
            datetime(2026, 11, 1, hour, 30, 10, tzinfo=timezone.utc),
        )
        ctx = context(principal)
        service.admit(principal, ctx["request_id"])
        service.record_failure(ctx, 503, "test_cleanup")
        with pytest.raises(ExternalAPIError, match="rate_limit_exceeded"):
            service.admit(principal, uuid4().hex)
        with api["engine"].connect() as connection:
            row = connection.execute(select(usage)).mappings().one()
            assert row.Minute == datetime(2026, 11, 1, 1, 30)
            assert row.MinuteOffsetMinutes == offset


@pytest.mark.parametrize(
    "instant",
    [
        datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc),
        datetime(2026, 11, 1, 6, 30, tzinfo=timezone.utc),
        datetime(2026, 3, 8, 7, 30, tzinfo=timezone.utc),
    ],
)
def test_local_timestamp_and_offset_round_trip(instant: datetime) -> None:
    """Round-trip real instants without persisting aware or UTC datetimes."""
    assert (
        restore_instant(eastern_naive(instant), eastern_offset(instant))
        == instant
    )
