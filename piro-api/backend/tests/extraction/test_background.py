import asyncio
import threading
import time
from types import SimpleNamespace

import anyio
import pytest
from fastapi.routing import run_endpoint_function
from starlette.background import BackgroundTask

from apis.version1 import route_extraction
from core.extraction_worker import ExtractionWorkerPool


@pytest.mark.parametrize("operation", ["cancel", "clear"])
def test_session_lock_wait_does_not_block_web_event_loop(
    monkeypatch, operation
):
    entered = threading.Event()
    release = threading.Event()
    monkeypatch.setattr(
        route_extraction, "_require_session_ownership", lambda *args: None
    )

    def wait_for_session_lock(*args, **kwargs):
        entered.set()
        assert release.wait(timeout=5)
        return None

    if operation == "cancel":
        endpoint = route_extraction.cancel_extraction
        monkeypatch.setattr(
            route_extraction, "lock_extraction_session", wait_for_session_lock
        )
        monkeypatch.setattr(
            route_extraction,
            "get_latest_run",
            lambda *args: SimpleNamespace(
                Status="running",
                ExtractionRunId=2,
            ),
        )
        monkeypatch.setattr(
            route_extraction,
            "request_run_cancellation",
            lambda *args: "cancelled",
        )
    else:
        endpoint = route_extraction.clear_queue_endpoint
        monkeypatch.setattr(
            route_extraction, "reclaim_stale_run", wait_for_session_lock
        )
        monkeypatch.setattr(route_extraction, "clear_queue", lambda *args: 1)

    async def exercise():
        task = asyncio.create_task(
            run_endpoint_function(
                dependant=SimpleNamespace(call=endpoint),
                values={"session_id": 1, "current_user_id": 1, "db": None},
                is_coroutine=asyncio.iscoroutinefunction(endpoint),
            )
        )
        try:
            while not entered.is_set():
                await asyncio.sleep(0.01)
            # This coroutine must still execute while the DB lock is held.
            await asyncio.sleep(0.02)
            assert not task.done()
        finally:
            release.set()
            await task

    asyncio.run(asyncio.wait_for(exercise(), timeout=5))


def test_blocking_extraction_runs_without_blocking_web_event_loop(monkeypatch):
    thread_ids = []
    finished = threading.Event()

    async def blocking_job(*args):
        thread_ids.append(threading.get_ident())
        # Models a synchronous ORM call in the extraction coroutine.
        time.sleep(0.2)
        finished.set()

    monkeypatch.setattr(
        route_extraction, "_run_extraction_job_async", blocking_job
    )

    async def exercise_background_task():
        web_thread = threading.get_ident()
        background = asyncio.create_task(
            BackgroundTask(
                route_extraction._run_extraction_job,
                1,
                2,
                "pytest",
                "ANALYST",
            )()
        )
        responsive_ticks = 0
        while not finished.is_set():
            await asyncio.sleep(0.01)
            responsive_ticks += 1
        await background
        assert responsive_ticks >= 5
        assert len(thread_ids) == 1
        assert thread_ids[0] != web_thread

    asyncio.run(asyncio.wait_for(exercise_background_task(), timeout=5))


def test_extractions_are_bounded_without_borrowing_web_thread_tokens():
    pool = ExtractionWorkerPool(max_workers=2)
    release = threading.Event()
    started = []
    lock = threading.Lock()

    async def blocking_job():
        with lock:
            started.append(threading.get_ident())
        assert release.wait(timeout=5)

    async def exercise():
        limiter = anyio.to_thread.current_default_thread_limiter()
        old_limit = limiter.total_tokens
        limiter.total_tokens = 1
        tasks = [asyncio.create_task(pool.run(blocking_job)) for _ in range(3)]
        try:
            while len(started) < 2:
                await asyncio.sleep(0.01)
            await asyncio.sleep(0.05)
            assert len(started) == 2
            assert limiter.borrowed_tokens == 0
            assert (
                await asyncio.wait_for(
                    anyio.to_thread.run_sync(lambda: "web request completed"),
                    timeout=1,
                )
                == "web request completed"
            )
        finally:
            release.set()
            await asyncio.gather(*tasks)
            limiter.total_tokens = old_limit
        assert len(started) == 3
        assert len(set(started)) == 2

    try:
        asyncio.run(asyncio.wait_for(exercise(), timeout=5))
    finally:
        release.set()
        pool.shutdown()


def test_request_cancellation_reaches_worker_and_finishes_cleanup():
    pool = ExtractionWorkerPool(max_workers=1)
    started = threading.Event()
    cleaned_up = threading.Event()

    async def job():
        started.set()
        try:
            await asyncio.sleep(30)
        finally:
            cleaned_up.set()

    async def exercise():
        task = asyncio.create_task(pool.run(job))
        while not started.is_set():
            await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cleaned_up.is_set()

    try:
        asyncio.run(asyncio.wait_for(exercise(), timeout=5))
    finally:
        pool.shutdown()
