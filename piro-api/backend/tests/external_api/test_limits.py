from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from time import monotonic
from uuid import uuid4

import pytest
from apis.external_api.context import RequestContext
from apis.external_api.errors import ExternalAPIError
from apis.external_api.models import ExternalApiLease, ExternalApiUsage
from apis.external_api.security import Principal
from apis.external_api.service import ExternalService
from apis.external_api.timeutil import eastern_day, seconds_until_reset
from apis.external_api.v1.schemas import SearchResponse
from db.engine import create_database_engine
from sqlalchemy import select, update

from tests.external_api.types import ApiFixture


def context(principal: Principal) -> RequestContext:
    """Build request metadata for direct service tests."""
    return {
        "request_id": uuid4().hex,
        "principal": principal,
        "started": monotonic(),
    }


def test_concurrency_limit_is_shared_across_independent_pools_and_keys(
    api: ApiFixture,
) -> None:
    """Verify concurrency limit is shared across independent pools and keys."""
    from apis.external_api.admin import issue_key

    other_key = issue_key(api["engine"], api["client_id"], "pytest")
    second_engine = create_database_engine(
        api["engine"].url, query_timeout_seconds=30
    ).execution_options(**api["engine"].get_execution_options())
    try:
        services: list[ExternalService] = [
            api["app"].state.service,
            ExternalService(second_engine, api["config"]),
        ]
        principals: list[Principal] = [
            services[0].authenticate(api["credential"]["api_key"]),
            services[1].authenticate(other_key["api_key"]),
        ]
        api["config"].max_concurrent = 1
        barrier = Barrier(2)

        def attempt(index: int) -> tuple[str, RequestContext]:
            """Race an admission against another independent connection
            pool."""
            ctx = context(principals[index])
            barrier.wait()
            try:
                services[index].admit(principals[index], ctx["request_id"])
                return "admitted", ctx
            except ExternalAPIError as exc:
                return exc.code, ctx

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (0, 1)))
        assert sorted(item[0] for item in results) == [
            "admitted",
            "concurrency_limit_exceeded",
        ]
        with api["engine"].connect() as connection:
            assert len(connection.execute(select(ExternalApiLease)).all()) == 1
        for status, ctx in results:
            if status == "admitted":
                services[0].record_failure(ctx, 503, "test_cleanup")
        with api["engine"].connect() as connection:
            assert len(connection.execute(select(ExternalApiLease)).all()) == 0
    finally:
        second_engine.dispose()


def test_simultaneous_completions_cannot_overspend_daily_quota(
    api: ApiFixture,
) -> None:
    """Verify simultaneous completions cannot overspend daily quota."""
    service: ExternalService = api["app"].state.service
    principal = service.authenticate(api["credential"]["api_key"])
    api["config"].daily_records = 1
    contexts: list[RequestContext] = [context(principal), context(principal)]
    for ctx in contexts:
        service.admit(principal, ctx["request_id"])
    barrier = Barrier(2)

    def complete(ctx: RequestContext) -> str:
        """Race quota completion against another admitted request."""
        barrier.wait()
        try:
            # The service only accounts for the already validated response;
            # endpoint tests verify that record_count equals returned rows.
            service.complete(
                ctx,
                SearchResponse(
                    request_id=ctx["request_id"],
                    data=[],
                    cases=[],
                    record_count=1,
                ),
            )
            return "success"
        except ExternalAPIError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(complete, contexts))
    assert sorted(result) == ["daily_quota_exceeded", "success"]
    with api["engine"].connect() as connection:
        assert connection.scalar(select(ExternalApiUsage.ReturnedRecords)) == 1
        assert connection.scalar(select(ExternalApiLease.RequestId)) is None


def test_expired_worker_lease_is_recovered_and_old_worker_cannot_complete(
    api: ApiFixture,
) -> None:
    """Verify expired worker lease is recovered and old worker cannot
    complete."""
    service: ExternalService = api["app"].state.service
    principal = service.authenticate(api["credential"]["api_key"])
    api["config"].max_concurrent = 1
    old = context(principal)
    service.admit(principal, old["request_id"])
    with api["engine"].begin() as connection:
        connection.execute(
            update(ExternalApiLease).values(ExpiresAt=datetime(2000, 1, 1))
        )
    new = context(principal)
    service.admit(principal, new["request_id"])
    with pytest.raises(ExternalAPIError, match="request_lease_expired"):
        service.complete(
            old,
            SearchResponse(
                request_id=old["request_id"], data=[], cases=[], record_count=0
            ),
        )
    service.record_failure(new, 503, "test_cleanup")


@pytest.mark.parametrize(
    "now,expected_day,reset",
    [
        (
            datetime(2026, 3, 8, 5, tzinfo=timezone.utc),
            "2026-03-08",
            23 * 3600,
        ),
        (
            datetime(2026, 11, 1, 4, tzinfo=timezone.utc),
            "2026-11-01",
            25 * 3600,
        ),
        (
            datetime(2026, 10, 6, 3, 59, 59, tzinfo=timezone.utc),
            "2026-10-05",
            1,
        ),
    ],
)
def test_eastern_quota_days_include_dst(
    now: datetime, expected_day: str, reset: int
) -> None:
    """Verify eastern quota days include dst."""
    assert eastern_day(now).isoformat() == expected_day
    assert seconds_until_reset(now) == reset


def test_quota_and_minute_reset_and_midnight_completion(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify quota and minute reset and midnight completion."""
    service: ExternalService = api["app"].state.service
    principal = service.authenticate(api["credential"]["api_key"])
    now = datetime(2026, 10, 6, 3, 59, 59, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "apis.external_api.service.database_now", lambda _connection: now
    )
    ctx = context(principal)
    service.admit(principal, ctx["request_id"])
    with api["engine"].begin() as connection:
        connection.execute(
            update(ExternalApiUsage).values(
                ReturnedRecords=api["config"].daily_records
            )
        )
    now += timedelta(seconds=2)
    service.complete(
        ctx,
        SearchResponse(
            request_id=ctx["request_id"], data=[], cases=[], record_count=1
        ),
    )
    with api["engine"].connect() as connection:
        row = connection.execute(select(ExternalApiUsage)).mappings().one()
        assert str(row.QuotaDay) == "2026-10-06"
        assert row.ReturnedRecords == 1
    next_request = context(principal)
    service.admit(principal, next_request["request_id"])
    with api["engine"].connect() as connection:
        assert connection.scalar(select(ExternalApiUsage.RequestCount)) == 1
    service.record_failure(next_request, 503, "test_cleanup")


def test_rate_limit_is_shared_after_service_restart(api: ApiFixture) -> None:
    """Verify rate limit is shared after service restart."""
    service: ExternalService = api["app"].state.service
    api["config"].requests_per_minute = 1
    principal = service.authenticate(api["credential"]["api_key"])
    ctx = context(principal)
    service.admit(principal, ctx["request_id"])
    service.record_failure(ctx, 503, "test_cleanup")
    restarted = ExternalService(api["engine"], api["config"])
    with pytest.raises(ExternalAPIError, match="rate_limit_exceeded"):
        restarted.admit(principal, uuid4().hex)
