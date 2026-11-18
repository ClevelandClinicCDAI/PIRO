# Extraction worker concurrency and recovery

Each API process has a dedicated pool of two extraction threads. The full
job, including synchronous SQLAlchemy operations and the LLM coroutine's
event loop, runs in one of those threads. Additional jobs wait in that pool's
queue without taking Starlette/AnyIO's shared request-worker tokens. With
the checked-in four-process Gunicorn service, up to eight jobs run at once.
The waiting queue is in memory and has no size limit; this is not a durable
job service.

Run startup, retry, cancellation, and queue clearing use synchronous FastAPI
endpoints, so database lock waits happen in request-worker threads rather
than the web event loop. Cancelling the background task forwards cancellation
to its extraction thread's event loop and allows database cleanup to run.
The cancellation endpoint still requests cooperative cancellation between
cases.

Status polling only reads state. `is_stale` reports more than 30 minutes
without run/queue activity; inactivity alone does not change the run. A
subsequent start, retry, or queue-clear request can recover an inactive run.
Recovery sets its cancellation flag and failed status under a database lock
on the extraction session. Admission retains that lock through creating the
replacement run. Every extraction worker write transaction obtains the same
lock and verifies that its run is still the latest active run. A delayed
worker can finish an already-issued provider call, but cannot persist its
results or overwrite the successor's queue/session status after recovery.
Locks are released between write transactions, including during LLM calls.

PostgreSQL uses `FOR UPDATE`; SQL Server uses `UPDLOCK, HOLDLOCK` because it
does not implement SQLAlchemy's `FOR UPDATE`. SQLite uses `BEGIN IMMEDIATE`
for its write transaction. No schema change is required.

Before relying on recovery during deployment, drain or stop processes running
the older implementation: those workers do not honor the new write fence.
Jobs remain process-local and are not automatically resumed after a restart;
inactive requests can be retried through the existing workflow after recovery.

Regression coverage includes read-only polling, delayed worker results/errors/
cancellation after replacement, serialized simultaneous starts and recovery,
and thread-pool isolation. Cross-connection locking is exercised on localhost
PostgreSQL. SQL Server lock hints are verified by statement compilation; this
suite does not exercise a live SQL Server.
