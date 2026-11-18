import asyncio
import threading
import time

from starlette.background import BackgroundTask

from apis.version1 import route_extraction


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
