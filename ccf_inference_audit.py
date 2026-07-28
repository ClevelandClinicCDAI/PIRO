"""Durable local audit outbox with opportunistic batched delivery.

The client intentionally has no third-party dependencies so it can be vendored
into Airflow, Celery, API, and CLI applications. Clinical content must never be
passed in ``attributes``. Identifiers are HMAC-hashed before they enter the
outbox.
"""

from __future__ import annotations

import atexit
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import sqlite3
import threading
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid


LOGGER = logging.getLogger("ccf_inference_audit")
SCHEMA_VERSION = 1
VALID_KINDS = {"inference", "work_item", "run", "query", "action"}
VALID_STATUSES = {"started", "succeeded", "failed", "cancelled", "partial"}
_SENSITIVE_ATTRIBUTE_KEYS = {
    "accession",
    "accession_number",
    "date_of_birth",
    "dob",
    "full_name",
    "generated_sql",
    "mrn",
    "name",
    "model_output",
    "output",
    "patient",
    "patient_name",
    "prompt",
    "raw_sql",
    "report",
    "response",
    "sql",
    "text",
}
_SENSITIVE_ATTRIBUTE_SUFFIXES = ("_prompt", "_report", "_response", "_sql", "_text")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_dimension(value: Any, *, limit: int = 160) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:limit]


def _clean_attributes(attributes: Mapping[str, Any] | None) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for raw_key, value in (attributes or {}).items():
        key = str(raw_key).strip()
        folded = key.casefold()
        if (
            not key
            or folded in _SENSITIVE_ATTRIBUTE_KEYS
            or folded.endswith(_SENSITIVE_ATTRIBUTE_SUFFIXES)
        ):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[key[:80]] = value if not isinstance(value, str) else value[:500]
        elif isinstance(value, (list, tuple)):
            cleaned[key[:80]] = [
                item if isinstance(item, (int, float, bool)) or item is None else str(item)[:160]
                for item in value[:50]
            ]
    return cleaned


def _nested_value(source: Any, *paths: str) -> int | None:
    for path in paths:
        value = source
        for part in path.split("."):
            if isinstance(value, Mapping):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            if value is None:
                break
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def token_usage_from_response(response: Any) -> dict[str, int | None]:
    """Normalize OpenAI, Gemini, Ollama, and Agent Framework usage objects."""
    usage = (
        getattr(response, "usage", None)
        or getattr(response, "usage_metadata", None)
        or getattr(response, "usage_details", None)
        or (response.get("usage") if isinstance(response, Mapping) else None)
        or (response.get("usage_metadata") if isinstance(response, Mapping) else None)
        or {}
    )
    input_tokens = _nested_value(
        usage,
        "prompt_tokens",
        "prompt_token_count",
        "input_tokens",
        "input_token_count",
    )
    output_tokens = _nested_value(
        usage,
        "completion_tokens",
        "candidates_token_count",
        "output_tokens",
        "output_token_count",
    )
    total_tokens = _nested_value(usage, "total_tokens", "total_token_count")
    cached_tokens = _nested_value(
        usage,
        "cached_content_token_count",
        "prompt_tokens_details.cached_tokens",
        "input_token_details.cached_tokens",
    )
    reasoning_tokens = _nested_value(
        usage,
        "thoughts_token_count",
        "completion_tokens_details.reasoning_tokens",
        "output_token_details.reasoning_tokens",
    )
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "reasoning_tokens": reasoning_tokens,
    }


class AuditClient:
    """Write events locally first, then flush them to the central collector."""

    def __init__(
        self,
        application_id: str,
        *,
        environment: str = "development",
        endpoint: str | None = None,
        token: str | None = None,
        hash_key: str | None = None,
        sqlite_path: str | Path | None = None,
        app_version: str | None = None,
        flush_batch_size: int = 100,
        request_timeout_seconds: float = 2.0,
    ) -> None:
        self.application_id = application_id.strip()
        if not self.application_id:
            raise ValueError("application_id is required")
        self.environment = environment.strip() or "development"
        self.endpoint = endpoint.rstrip("/") if endpoint else None
        self.token = token
        self.hash_key = hash_key.encode("utf-8") if hash_key else None
        self.app_version = app_version
        self.flush_batch_size = max(1, min(int(flush_batch_size), 500))
        self.request_timeout_seconds = max(0.1, float(request_timeout_seconds))
        default_path = Path(os.getenv("INFERENCE_AUDIT_DATA_DIR", ".inference-audit")) / (
            f"{self.application_id}.sqlite3"
        )
        self.sqlite_path = Path(sqlite_path or default_path)
        self._lock = threading.RLock()
        self._flush_lock = threading.Lock()
        self._flush_thread_lock = threading.Lock()
        self._flush_thread: threading.Thread | None = None
        self._initialized = False
        self._warned_missing_hash_key = False
        atexit.register(self.flush_all)

    @classmethod
    def from_env(cls, application_id: str, *, app_version: str | None = None) -> "AuditClient":
        prefix = "INFERENCE_AUDIT_"
        sqlite_path = os.getenv(f"{prefix}SQLITE_PATH")
        if not sqlite_path:
            data_dir = Path(os.getenv(f"{prefix}DATA_DIR", ".inference-audit"))
            sqlite_path = str(data_dir / f"{application_id}.sqlite3")
        return cls(
            application_id,
            environment=os.getenv(f"{prefix}ENVIRONMENT", os.getenv("APP_ENV", "development")),
            endpoint=os.getenv(f"{prefix}ENDPOINT"),
            token=os.getenv(f"{prefix}TOKEN"),
            hash_key=os.getenv(f"{prefix}HASH_KEY"),
            sqlite_path=sqlite_path,
            app_version=app_version or os.getenv("APP_VERSION") or os.getenv("GIT_SHA"),
            flush_batch_size=int(os.getenv(f"{prefix}BATCH_SIZE", "100")),
            request_timeout_seconds=float(os.getenv(f"{prefix}TIMEOUT_SECONDS", "2")),
        )

    def hash_identifier(self, identifier: Any, *, namespace: str) -> str | None:
        if identifier is None or str(identifier).strip() == "":
            return None
        if self.hash_key is None:
            if not self._warned_missing_hash_key:
                LOGGER.warning(
                    "INFERENCE_AUDIT_HASH_KEY is unset; identifiers will be omitted from audit events"
                )
                self._warned_missing_hash_key = True
            return None
        canonical = f"{namespace.strip().casefold()}:{str(identifier).strip().casefold()}"
        return hmac.new(self.hash_key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    def emit(
        self,
        *,
        event_kind: str,
        event_name: str,
        status: str,
        event_id: str | None = None,
        event_time: str | None = None,
        trace_id: str | None = None,
        run_id: str | None = None,
        parent_event_id: str | None = None,
        actor_id: Any = None,
        subject_type: str | None = None,
        subject_id: Any = None,
        work_item_type: str | None = None,
        work_item_id: Any = None,
        provider: str | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        deployment: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        cached_tokens: int | None = None,
        reasoning_tokens: int | None = None,
        input_units: float | None = None,
        output_units: float | None = None,
        duration_ms: float | None = None,
        retry_count: int = 0,
        metric_name: str | None = None,
        metric_value: float | None = None,
        provider_request_id: str | None = None,
        error_category: str | None = None,
        error_code: str | None = None,
        attributes: Mapping[str, Any] | None = None,
        flush: bool = True,
    ) -> str:
        if event_kind not in VALID_KINDS:
            raise ValueError(f"event_kind must be one of {sorted(VALID_KINDS)}")
        if status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")

        normalized_total = total_tokens
        if normalized_total is None and input_tokens is not None and output_tokens is not None:
            normalized_total = input_tokens + output_tokens

        resolved_event_id = event_id or str(uuid.uuid4())
        payload = {
            "schema_version": SCHEMA_VERSION,
            "event_id": resolved_event_id,
            "event_time": event_time or _utc_now(),
            "application_id": self.application_id,
            "environment": self.environment,
            "app_version": _clean_dimension(self.app_version),
            "event_kind": event_kind,
            "event_name": _clean_dimension(event_name),
            "status": status,
            "trace_id": _clean_dimension(trace_id),
            "run_id": _clean_dimension(run_id),
            "parent_event_id": _clean_dimension(parent_event_id),
            "actor_hash": self.hash_identifier(actor_id, namespace="actor"),
            "subject_type": _clean_dimension(subject_type),
            "subject_hash": self.hash_identifier(subject_id, namespace=subject_type or "subject"),
            "work_item_type": _clean_dimension(work_item_type),
            "work_item_hash": self.hash_identifier(
                work_item_id, namespace=work_item_type or "work-item"
            ),
            "provider": _clean_dimension(provider),
            "model_name": _clean_dimension(model_name),
            "model_version": _clean_dimension(model_version),
            "deployment": _clean_dimension(deployment),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": normalized_total,
            "cached_tokens": cached_tokens,
            "reasoning_tokens": reasoning_tokens,
            "input_units": input_units,
            "output_units": output_units,
            "duration_ms": duration_ms,
            "retry_count": max(0, int(retry_count)),
            "metric_name": _clean_dimension(metric_name),
            "metric_value": metric_value,
            "provider_request_id": _clean_dimension(provider_request_id),
            "error_category": _clean_dimension(error_category),
            "error_code": _clean_dimension(error_code),
            "attributes": _clean_attributes(attributes),
        }
        self._enqueue(payload)
        if flush and self.endpoint and self.token:
            self._schedule_flush()
        return resolved_event_id

    def inference(self, *, event_name: str = "model_inference", **kwargs: Any) -> str:
        return self.emit(event_kind="inference", event_name=event_name, **kwargs)

    def work_item(self, *, event_name: str = "work_item_processed", **kwargs: Any) -> str:
        return self.emit(event_kind="work_item", event_name=event_name, **kwargs)

    def run(self, *, event_name: str = "run", **kwargs: Any) -> str:
        return self.emit(event_kind="run", event_name=event_name, **kwargs)

    def span(self, *, event_kind: str, event_name: str, **kwargs: Any) -> "AuditSpan":
        return AuditSpan(self, event_kind=event_kind, event_name=event_name, fields=kwargs)

    def pending_count(self) -> int:
        try:
            self._ensure_schema()
            with self._connect() as connection:
                row = connection.execute("SELECT COUNT(*) FROM audit_outbox").fetchone()
                return int(row[0]) if row else 0
        except Exception:
            LOGGER.exception("Could not inspect inference audit outbox")
            return -1

    def flush(self) -> int:
        if not self.endpoint or not self.token or not self._flush_lock.acquire(blocking=False):
            return 0
        try:
            rows = self._load_batch()
            if not rows:
                return 0
            body = json.dumps({"events": [json.loads(row["payload_json"]) for row in rows]}).encode(
                "utf-8"
            )
            request = Request(
                f"{self.endpoint}/api/v1/events/batch",
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "User-Agent": f"ccf-inference-audit/{SCHEMA_VERSION}",
                },
            )
            try:
                with urlopen(request, timeout=self.request_timeout_seconds) as response:
                    if response.status < 200 or response.status >= 300:
                        raise RuntimeError(f"collector returned HTTP {response.status}")
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                self._mark_failed([row["event_id"] for row in rows], type(exc).__name__)
                return 0
            self._delete_batch([row["event_id"] for row in rows])
            return len(rows)
        except Exception:
            LOGGER.exception("Inference audit flush failed; events remain in the local outbox")
            return 0
        finally:
            self._flush_lock.release()

    def flush_all(self, max_batches: int = 20) -> int:
        delivered = 0
        for _ in range(max(1, max_batches)):
            count = self.flush()
            delivered += count
            if count == 0:
                break
        return delivered

    def _schedule_flush(self) -> None:
        with self._flush_thread_lock:
            if self._flush_thread is not None and self._flush_thread.is_alive():
                return
            self._flush_thread = threading.Thread(
                target=self.flush_all,
                kwargs={"max_batches": 10},
                daemon=True,
                name="inference-audit-flush",
            )
            self._flush_thread.start()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.sqlite_path), timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def _ensure_schema(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_outbox (
                        event_id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        next_attempt_at REAL NOT NULL DEFAULT 0,
                        last_error TEXT
                    )
                    """
                )
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS idx_audit_outbox_retry "
                    "ON audit_outbox(next_attempt_at, created_at)"
                )
            self._initialized = True

    def _enqueue(self, payload: Mapping[str, Any]) -> None:
        try:
            self._ensure_schema()
            serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            with self._lock, self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO audit_outbox
                        (event_id, created_at, payload_json, attempts, next_attempt_at)
                    VALUES (?, ?, ?, 0, 0)
                    """,
                    (payload["event_id"], _utc_now(), serialized),
                )
        except Exception:
            LOGGER.exception("Inference audit event could not be persisted locally")

    def _load_batch(self) -> list[sqlite3.Row]:
        self._ensure_schema()
        with self._lock, self._connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT event_id, payload_json
                    FROM audit_outbox
                    WHERE next_attempt_at <= ?
                    ORDER BY created_at
                    LIMIT ?
                    """,
                    (time.time(), self.flush_batch_size),
                ).fetchall()
            )

    def _delete_batch(self, event_ids: list[str]) -> None:
        if not event_ids:
            return
        placeholders = ",".join("?" for _ in event_ids)
        with self._lock, self._connect() as connection:
            connection.execute(
                f"DELETE FROM audit_outbox WHERE event_id IN ({placeholders})", event_ids
            )

    def _mark_failed(self, event_ids: list[str], error: str) -> None:
        if not event_ids:
            return
        with self._lock, self._connect() as connection:
            for event_id in event_ids:
                row = connection.execute(
                    "SELECT attempts FROM audit_outbox WHERE event_id = ?", (event_id,)
                ).fetchone()
                attempts = (int(row[0]) if row else 0) + 1
                backoff = min(300.0, float(2 ** min(attempts, 8)))
                connection.execute(
                    """
                    UPDATE audit_outbox
                    SET attempts = ?, next_attempt_at = ?, last_error = ?
                    WHERE event_id = ?
                    """,
                    (attempts, time.time() + backoff, error[:160], event_id),
                )


@dataclass
class AuditSpan(AbstractContextManager["AuditSpan"]):
    client: AuditClient
    event_kind: str
    event_name: str
    fields: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.monotonic)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __enter__(self) -> "AuditSpan":
        return self

    def __exit__(self, exc_type: Any, exc: BaseException | None, traceback: Any) -> bool:
        fields = dict(self.fields)
        fields["duration_ms"] = round((time.monotonic() - self.started_at) * 1000, 3)
        fields["event_id"] = self.event_id
        if exc is None:
            fields.setdefault("status", "succeeded")
        else:
            fields["status"] = "failed"
            fields.setdefault("error_category", type(exc).__name__)
        self.client.emit(event_kind=self.event_kind, event_name=self.event_name, **fields)
        return False
