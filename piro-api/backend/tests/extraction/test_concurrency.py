import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import event, func
from sqlalchemy.dialects import mssql
from sqlalchemy.orm import sessionmaker

from apis.version1 import route_extraction
from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.repository import extraction
from tests.extraction.test_persistence import (
    comment,
    field,
    make_stale,
    state as persistence_state,
)
from viewmodel.extraction import ExtractionRunRequest

# Share the realistic persistence fixture, including both database backends.
state = persistence_state


def test_polling_detects_inactivity_without_revoking_worker(
    state, monkeypatch
):
    make_stale(state)
    monkeypatch.setattr(
        route_extraction, "_require_session_status_access", lambda *args: None
    )
    statements = []

    def record_sql(connection, cursor, statement, parameters, context, many):
        statements.append(statement)

    engine = state.db.get_bind()
    event.listen(engine, "before_cursor_execute", record_sql)
    try:
        for _ in range(2):
            status = asyncio.run(
                route_extraction.get_status(
                    state.session_id,
                    1,
                    "ANALYST",
                    state.db,
                )
            )
            assert status["status"] == "running"
            assert status["is_stale"]
    finally:
        event.remove(engine, "before_cursor_execute", record_sql)
    assert not any(
        sql.lstrip().upper().startswith(("UPDATE", "DELETE", "INSERT"))
        for sql in statements
    )
    assert not state.db.get(ExtractionRun, state.run_id).CancellationRequested
    assert (
        state.db.query(ExtractionQueue).filter_by(CaseId=101).one().Status
        == "running"
    )


@pytest.mark.parametrize("outcome", ["result", "error", "cancelled"])
def test_delayed_worker_cannot_write_after_recovery_and_replacement(
    state,
    monkeypatch,
    outcome,
):
    comment(state, "Grade: 2")
    sessions = sessionmaker(bind=state.db.get_bind(), autoflush=False)
    replacement_ids = []

    class DelayedLlm:
        async def extract(self, text, schema):
            with sessions() as recovery:
                old = datetime.now(timezone.utc) - timedelta(hours=1)
                recovery.query(ExtractionRun).filter_by(
                    ExtractionRunId=state.run_id
                ).update(
                    {"StartedAt": old, "CreateDate": old},
                    synchronize_session=False,
                )
                recovery.query(ExtractionQueue).update(
                    {"UpdateDate": old}, synchronize_session=False
                )
                recovery.commit()
                extraction.reclaim_stale_run(
                    state.session_id, recovery, commit=False
                )
                replacement = extraction.create_run(
                    state.session_id,
                    '{"grade": {}}',
                    "test",
                    "test",
                    "pytest",
                    recovery,
                    commit=False,
                )
                replacement_ids.append(replacement.ExtractionRunId)
                extraction.update_run_status(
                    replacement.ExtractionRunId,
                    "running",
                    recovery,
                    commit=False,
                )
                extraction.update_session_status(
                    state.session_id, "running", recovery, commit=False
                )
                recovery.query(ExtractionQueue).filter_by(CaseId=101).update(
                    {
                        "Status": "running",
                        "AttemptCount": 77,
                        "ErrorMessage": "new worker",
                    },
                    synchronize_session=False,
                )
                recovery.commit()
            if outcome == "error":
                raise RuntimeError("delayed provider failed")
            if outcome == "cancelled":
                raise asyncio.CancelledError
            return {"grade": field()}

    monkeypatch.setattr(route_extraction, "get_llm_client", DelayedLlm)
    work = route_extraction._run_extraction_job_async(
        state.session_id,
        state.run_id,
        "pytest",
        "ANALYST",
        case_ids=[101],
    )
    if outcome == "cancelled":
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(work)
    else:
        asyncio.run(work)
    old = state.db.get(ExtractionRun, state.run_id)
    assert old.Status == "failed"
    assert old.CancellationRequested
    assert state.db.get(ExtractionRun, replacement_ids[0]).Status == "running"
    assert (
        state.db.get(ExtractionSession, state.session_id).Status == "running"
    )
    assert state.db.query(extraction.ExtractionResult).count() == 0
    queue = state.db.query(ExtractionQueue).filter_by(CaseId=101).one()
    assert (queue.Status, queue.AttemptCount, queue.ErrorMessage) == (
        "running",
        77,
        "new worker",
    )


def test_fenced_worker_cannot_reactivate_itself(state, monkeypatch):
    make_stale(state)
    extraction.reclaim_stale_run(state.session_id, state.db)

    def unexpected_provider():
        pytest.fail("A fenced worker must stop before contacting the LLM")

    monkeypatch.setattr(
        route_extraction, "get_llm_client", unexpected_provider
    )
    asyncio.run(
        route_extraction._run_extraction_job_async(
            state.session_id,
            state.run_id,
            "pytest",
            "ANALYST",
        )
    )
    assert state.db.get(ExtractionRun, state.run_id).Status == "failed"
    assert state.db.get(ExtractionSession, state.session_id).Status == "failed"


def test_session_lock_uses_sql_server_update_and_transaction_hints(state):
    statements = []

    def record_sql(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(context.compiled.statement)

    engine = state.db.get_bind()
    event.listen(engine, "before_cursor_execute", record_sql)
    try:
        extraction.lock_extraction_session(state.session_id, state.db)
    finally:
        event.remove(engine, "before_cursor_execute", record_sql)
        state.db.rollback()
    sql = str(statements[-1].compile(dialect=mssql.dialect()))
    assert "WITH (UPDLOCK, HOLDLOCK)" in sql


def test_simultaneous_run_starts_admit_only_one_postgresql(state, monkeypatch):
    if state.db.get_bind().dialect.name != "postgresql":
        pytest.skip("Cross-connection row-lock test requires PostgreSQL")
    extraction.update_run_status(state.run_id, "completed", state.db)
    sessions = sessionmaker(bind=state.db.get_bind(), autoflush=False)
    barrier = threading.Barrier(2)

    def start():
        with sessions() as db:
            barrier.wait(timeout=5)
            try:
                run = route_extraction.start_extraction(
                    ExtractionRunRequest(session_id=state.session_id),
                    BackgroundTasks(),
                    "pytest",
                    1,
                    "ANALYST",
                    db,
                )
                return run.ExtractionRunId
            except HTTPException as exc:
                assert exc.status_code == 409
                return None

    with ThreadPoolExecutor(max_workers=2) as workers:
        first, second = [workers.submit(start) for _ in range(2)]
        outcomes = [first.result(timeout=10), second.result(timeout=10)]
    assert sum(value is not None for value in outcomes) == 1
    assert (
        state.db.query(ExtractionRun)
        .filter(ExtractionRun.Status.in_(("pending", "running")))
        .count()
        == 1
    )


def test_recovery_waits_for_guarded_case_transaction_postgresql(state):
    if state.db.get_bind().dialect.name != "postgresql":
        pytest.skip("Cross-connection row-lock test requires PostgreSQL")
    make_stale(state)
    sessions = sessionmaker(bind=state.db.get_bind(), autoflush=False)
    entered = threading.Event()
    extraction.require_run_ownership(state.session_id, state.run_id, state.db)

    def recover():
        with sessions() as db:
            entered.set()
            return extraction.reclaim_stale_run(state.session_id, db).Status

    with ThreadPoolExecutor(max_workers=1) as workers:
        future = workers.submit(recover)
        assert entered.wait(timeout=5)
        try:
            with pytest.raises(TimeoutError):
                future.result(timeout=0.1)
        finally:
            state.db.query(ExtractionQueue).filter_by(CaseId=101).update(
                {"UpdateDate": datetime.now(timezone.utc)},
                synchronize_session=False,
            )
            state.db.commit()
        assert future.result(timeout=5) == "running"


def test_admission_uses_run_order_after_earlier_transaction_postgresql(state):
    if state.db.get_bind().dialect.name != "postgresql":
        pytest.skip("Transaction-start timestamps are PostgreSQL-specific")
    extraction.update_run_status(state.run_id, "completed", state.db)
    sessions = sessionmaker(bind=state.db.get_bind(), autoflush=False)
    with sessions() as delayed, sessions() as other:
        # This transaction starts first, but creates its run last. PostgreSQL
        # now() retains the transaction-start time across the admission wait.
        transaction_start = delayed.query(func.now()).scalar()
        intermediate = extraction.create_run(
            state.session_id,
            '{"grade": {}}',
            "test",
            "test",
            "pytest",
            other,
        )
        assert intermediate.CreateDate > transaction_start
        intermediate_id = intermediate.ExtractionRunId
        extraction.update_run_status(intermediate_id, "completed", other)
        admitted = route_extraction.start_extraction(
            ExtractionRunRequest(session_id=state.session_id),
            BackgroundTasks(),
            "pytest",
            1,
            "ANALYST",
            delayed,
        )
        assert admitted.ExtractionRunId > intermediate_id
        assert admitted.CreateDate < intermediate.CreateDate
        assert (
            extraction.get_latest_run(
                state.session_id, delayed
            ).ExtractionRunId
            == admitted.ExtractionRunId
        )
        extraction.require_run_ownership(
            state.session_id, admitted.ExtractionRunId, delayed
        )
