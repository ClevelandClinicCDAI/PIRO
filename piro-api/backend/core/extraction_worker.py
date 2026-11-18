"""Extraction threads isolated from Starlette's shared request thread pool."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Awaitable, Callable


class _Cancellation:
    def __init__(self):
        self.lock = threading.Lock()
        self.requested = False
        self.loop = None
        self.task = None

    def register(self):
        with self.lock:
            self.loop = asyncio.get_running_loop()
            self.task = asyncio.current_task()
            if self.requested:
                self.loop.call_soon(self.task.cancel)

    def clear(self):
        with self.lock:
            self.loop = self.task = None

    def cancel(self):
        with self.lock:
            self.requested = True
            if self.loop is not None:
                self.loop.call_soon_threadsafe(self.task.cancel)


class ExtractionWorkerPool:
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="piro-extraction"
        )

    async def run(self, job: Callable[[], Awaitable[None]]) -> None:
        cancellation = _Cancellation()

        async def runner():
            cancellation.register()
            try:
                await job()
            finally:
                cancellation.clear()

        future = asyncio.get_running_loop().run_in_executor(
            self.executor, lambda: asyncio.run(runner())
        )
        try:
            await asyncio.shield(future)
        except asyncio.CancelledError:
            # Cancelling an executor Future cannot stop its thread. Forward
            # cancellation to the worker loop and let DB cleanup finish.
            cancellation.cancel()
            try:
                await asyncio.shield(future)
            except asyncio.CancelledError:
                pass
            raise

    def shutdown(self):
        self.executor.shutdown(wait=True)


# Per process: pending jobs wait here without taking AnyIO worker tokens.
extraction_workers = ExtractionWorkerPool(max_workers=2)
