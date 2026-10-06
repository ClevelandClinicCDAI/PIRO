import json
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from time import monotonic
from typing import Any

from sqlalchemy import (
    Select,
    String,
    delete,
    func,
    insert,
    literal,
    or_,
    select,
    union_all,
    update,
)
from sqlalchemy.engine import Connection, Engine, Row, RowMapping
from sqlalchemy.sql.selectable import Subquery

from .config import ExternalAPISettings
from .context import RequestContext
from .errors import ExternalAPIError
from .models import audits, cases, clients, keys, leases, orders, usage
from .security import SCOPE, Principal, authenticate
from .timeutil import (
    database_now,
    eastern_day,
    eastern_naive,
    eastern_offset,
    restore_instant,
    seconds_until_reset,
)
from .v1.schemas import (
    CaseResult,
    CaseStatus,
    LinkedOrder,
    SearchRequest,
    SearchResponse,
)


def lock_client(connection: Connection, client_id: str) -> None:
    """Serialize state changes for one integration until transaction commit."""
    # The UPDATE holds a row lock on SQL Server/PostgreSQL and serializes
    # writers on SQLite, including other workers and rotated keys.
    result = connection.execute(
        update(clients)
        .where(clients.c.ClientId == client_id)
        .values(IsActive=clients.c.IsActive)
    )
    if result.rowcount != 1:
        raise ExternalAPIError(
            403, "integration_disabled", "This integration is unavailable."
        )


def insert_request_audit(
    connection: Connection,
    context: RequestContext,
    status: int,
    code: str | None = None,
    response: SearchResponse | None = None,
) -> None:
    """Write request metadata without credentials or clinical result values."""
    principal: Principal | None = context.get("principal")
    connection.execute(
        insert(audits).values(
            RequestId=context["request_id"],
            ClientId=principal.client_id if principal else None,
            KeyId=principal.key_id if principal else context.get("key_id"),
            Event="request",
            OccurredAt=eastern_naive(database_now(connection)),
            Method=context.get("method"),
            Route=context.get("route"),
            SourceAddress=context.get("source_address"),
            CaseNumbersJson=json.dumps(context.get("case_numbers", [])),
            TestType=context.get("test_type"),
            CaseResultsJson=(
                json.dumps([case.dict() for case in response.cases])
                if response
                else None
            ),
            RecordCount=response.record_count if response else 0,
            StatusCode=status,
            ErrorCode=code,
            ElapsedMs=int((monotonic() - context["started"]) * 1000),
        )
    )


def escape_like(value: str) -> str:
    """Escape literal substrings for LIKE on supported database dialects."""
    # Backslash is our explicit ESCAPE character; '[' is also special on MSSQL.
    for char in ("\\", "%", "_", "["):
        value = value.replace(char, "\\" + char)
    return "%" + value + "%"


class ExternalService:
    """Coordinate linked-order reads, application access, limits, and audits."""

    def __init__(self, engine: Engine, config: ExternalAPISettings) -> None:
        """Bind an isolated pool and the external API resource limits."""
        self.engine: Engine = engine
        self.config: ExternalAPISettings = config

    def authenticate(self, value: str | None) -> Principal:
        """Verify an application key without human authentication dependencies."""
        with self.engine.connect() as connection:
            return authenticate(connection, value)

    def admit(self, principal: Principal, request_id: str) -> None:
        """Check shared limits and reserve a bounded concurrent request slot."""
        error: ExternalAPIError | None = None
        with self.engine.begin() as connection:
            lock_client(connection, principal.client_id)
            now: datetime = database_now(connection)
            active: bool | None = connection.scalar(
                select(clients.c.IsActive).where(
                    clients.c.ClientId == principal.client_id
                )
            )
            key: RowMapping = (
                connection.execute(
                    select(keys).where(keys.c.KeyId == principal.key_id)
                )
                .mappings()
                .one()
            )
            if (
                not active
                or key.RevokedAt is not None
                or restore_instant(key.ExpiresAt, key.ExpiresAtOffsetMinutes)
                <= now
            ):
                raise ExternalAPIError(
                    401, "invalid_api_key", "A valid X-API-Key is required."
                )
            if SCOPE not in principal.scope.split():
                raise ExternalAPIError(
                    403,
                    "insufficient_scope",
                    "This integration cannot read linked orders.",
                )
            state: RowMapping = (
                connection.execute(
                    select(usage).where(
                        usage.c.ClientId == principal.client_id
                    )
                )
                .mappings()
                .one()
            )
            day: date = eastern_day(now)
            minute: datetime = eastern_naive(now).replace(
                second=0, microsecond=0
            )
            offset: int = eastern_offset(now)
            count: int = (
                state.RequestCount
                if state.Minute == minute
                and state.MinuteOffsetMinutes == offset
                else 0
            )
            returned: int = (
                state.ReturnedRecords if state.QuotaDay == day else 0
            )
            connection.execute(
                update(usage)
                .where(usage.c.ClientId == principal.client_id)
                .values(
                    QuotaDay=day,
                    ReturnedRecords=returned,
                    Minute=minute,
                    MinuteOffsetMinutes=offset,
                    RequestCount=min(
                        count + 1, self.config.requests_per_minute + 1
                    ),
                )
            )
            # At most max_concurrent leases survive each admission. Compare
            # real instants in Python so both database dialects handle DST alike.
            existing: Sequence[RowMapping] = (
                connection.execute(
                    select(leases).where(
                        leases.c.ClientId == principal.client_id
                    )
                )
                .mappings()
                .all()
            )
            expired: list[str] = [
                lease.RequestId
                for lease in existing
                if restore_instant(
                    lease.ExpiresAt, lease.ExpiresAtOffsetMinutes
                )
                <= now
            ]
            if expired:
                connection.execute(
                    delete(leases).where(leases.c.RequestId.in_(expired))
                )
            active_count: int = len(existing) - len(expired)
            if count >= self.config.requests_per_minute:
                error = ExternalAPIError(
                    429,
                    "rate_limit_exceeded",
                    "Request rate limit exceeded.",
                    60 - now.second,
                )
            elif returned >= self.config.daily_records:
                error = ExternalAPIError(
                    429,
                    "daily_quota_exceeded",
                    "Daily returned-record quota exceeded.",
                    seconds_until_reset(now),
                )
            elif active_count >= self.config.max_concurrent:
                error = ExternalAPIError(
                    429,
                    "concurrency_limit_exceeded",
                    "Too many concurrent requests.",
                    5,
                )
            else:
                expiry: datetime = now + timedelta(
                    seconds=2 * self.config.query_timeout_seconds + 60
                )
                connection.execute(
                    insert(leases).values(
                        RequestId=request_id,
                        ClientId=principal.client_id,
                        ExpiresAt=eastern_naive(expiry),
                        ExpiresAtOffsetMinutes=eastern_offset(expiry),
                    )
                )
        # Rejected admissions still consume a request in the fixed
        # minute window.
        if error:
            raise error

    def search(self, body: SearchRequest, request_id: str) -> SearchResponse:
        """Read complete case batches and construct the stable v1 response."""
        if len(body.case_numbers) > self.config.max_cases:
            raise ExternalAPIError(
                422,
                "too_many_cases",
                f"Submit at most {self.config.max_cases} case numbers per request.",  # noqa:E501
            )
        requested: Subquery = union_all(
            *[
                select(
                    literal(index).label("position"),
                    literal(number, type_=String(100)).label("number"),
                )
                for index, number in enumerate(body.case_numbers)
            ]
        ).subquery("requested")
        # SQL performs the mapping so summaries respect the actual CaseNumber
        # collation. No Python lowercasing can incorrectly merge distinct
        # cases.
        case_query: Select[Any] = (
            select(requested.c.position, cases.c.CaseId)
            .select_from(
                requested.join(cases, cases.c.CaseNumber == requested.c.number)
            )
            .limit(self.config.max_records + 1)
        )
        query: Select[Any] = (
            select(
                cases.c.CaseNumber,
                cases.c.CaseId,
                orders.c.ComponentName,
                orders.c.ComponentExternalName,
                orders.c.ProcedureDesc,
                orders.c.DefaultUnit,
                orders.c.OrdValue,
                orders.c.OrdNumValue,
            )
            .select_from(cases.join(orders, cases.c.CaseId == orders.c.CaseId))
            .where(cases.c.CaseNumber.in_(body.case_numbers))
            .order_by(cases.c.CaseId, orders.c.LinkedOrderId)
            .limit(self.config.max_records + 1)
        )
        if body.test_type is not None:
            pattern: str = escape_like(body.test_type)
            columns = (
                orders.c.ComponentName,
                orders.c.ComponentExternalName,
                orders.c.ProcedureDesc,
            )
            if self.engine.dialect.name == "mssql":
                predicates = [
                    column.collate("Latin1_General_100_CI_AS").like(
                        pattern, escape="\\"
                    )
                    for column in columns
                ]
            else:
                predicates = [
                    func.lower(column).like(pattern.lower(), escape="\\")
                    for column in columns
                ]
            query = query.where(or_(*predicates))
        with self.engine.connect() as connection:
            found: Sequence[Row[Any]] = connection.execute(case_query).all()
            if len(found) > self.config.max_records:
                raise ExternalAPIError(
                    422,
                    "case_lookup_limit_exceeded",
                    "Too many matching PIRO cases; split the request.",
                )
            rows: Sequence[RowMapping] = (
                connection.execute(query).mappings().all()
            )
        if len(rows) > self.config.max_records:
            raise ExternalAPIError(
                422,
                "result_limit_exceeded",
                "Complete results exceed the batch limit; split case_numbers or narrow test_type.",  # noqa:E501
            )
        matched_ids: defaultdict[int, set[int]] = defaultdict(set)
        for position, case_id in found:
            matched_ids[position].add(case_id)
        counts: Counter[int] = Counter(row.CaseId for row in rows)
        data: list[LinkedOrder] = []
        for row in rows:
            value: dict[str, Any] = dict(row)
            value.pop("CaseId")
            if value["OrdNumValue"] is not None:
                value["OrdNumValue"] = format(value["OrdNumValue"], ".5f")
            data.append(LinkedOrder(**value))
        summaries: list[CaseResult] = []
        for position, number in enumerate(body.case_numbers):
            total: int = sum(
                counts[identifier] for identifier in matched_ids[position]
            )
            status: CaseStatus = (
                "matched"
                if total
                else (
                    "no_matching_orders"
                    if matched_ids[position]
                    else "case_not_found"
                )
            )
            summaries.append(
                CaseResult(
                    CaseNumber=number, status=status, record_count=total
                )
            )
        return SearchResponse(
            request_id=request_id,
            data=data,
            record_count=len(data),
            cases=summaries,
        )

    def complete(
        self, context: RequestContext, response: SearchResponse
    ) -> None:
        """Commit quota consumption and audit before releasing successful data."""
        principal: Principal = context["principal"]
        error: ExternalAPIError | None = None
        with self.engine.begin() as connection:
            lock_client(connection, principal.client_id)
            now: datetime = database_now(connection)
            lease: RowMapping | None = (
                connection.execute(
                    select(leases).where(
                        leases.c.RequestId == context["request_id"]
                    )
                )
                .mappings()
                .first()
            )
            connection.execute(
                delete(leases).where(
                    leases.c.RequestId == context["request_id"]
                )
            )
            state: RowMapping = (
                connection.execute(
                    select(usage).where(
                        usage.c.ClientId == principal.client_id
                    )
                )
                .mappings()
                .one()
            )
            returned: int = (
                state.ReturnedRecords
                if state.QuotaDay == eastern_day(now)
                else 0
            )
            if (
                lease is None
                or restore_instant(
                    lease.ExpiresAt, lease.ExpiresAtOffsetMinutes
                )
                <= now
            ):
                error = ExternalAPIError(
                    503,
                    "request_lease_expired",
                    "Request expired; retry the complete batch.",
                    5,
                )
            elif returned + response.record_count > self.config.daily_records:
                error = ExternalAPIError(
                    429,
                    "daily_quota_exceeded",
                    "Complete results exceed the remaining daily quota.",
                    seconds_until_reset(now),
                )
            else:
                connection.execute(
                    update(usage)
                    .where(usage.c.ClientId == principal.client_id)
                    .values(
                        QuotaDay=eastern_day(now),
                        ReturnedRecords=returned + response.record_count,
                    )
                )
                insert_request_audit(
                    connection, context, 200, response=response
                )
        if error:
            raise error
        context["audited"] = True

    def record_failure(
        self, context: RequestContext, status: int, code: str
    ) -> None:
        """Release a request lease and durably audit an unsuccessful request."""
        with self.engine.begin() as connection:
            principal: Principal | None = context.get("principal")
            if principal:
                lock_client(connection, principal.client_id)
                connection.execute(
                    delete(leases).where(
                        leases.c.RequestId == context["request_id"]
                    )
                )
            insert_request_audit(connection, context, status, code)
        context["audited"] = True
