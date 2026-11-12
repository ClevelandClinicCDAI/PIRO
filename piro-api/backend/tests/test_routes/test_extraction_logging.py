import asyncio
from io import StringIO
from types import SimpleNamespace

from apis.version1 import route_extraction
from piro_logger import logger


def _capture_logs():
    output = StringIO()
    handler_id = logger.add(
        output,
        format="{message}\n{exception}",
        diagnose=False,
    )
    return output, handler_id


def test_run_level_failure_logs_request_context_and_traceback(monkeypatch):
    db = SimpleNamespace(close=lambda: None)
    run_statuses = []
    output, handler_id = _capture_logs()

    def fail_to_create_client():
        raise RuntimeError("provider initialization failed")

    monkeypatch.setattr(route_extraction, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        route_extraction, "get_llm_client", fail_to_create_client
    )
    monkeypatch.setattr(
        route_extraction,
        "update_run_status",
        lambda run_id, status, db, error=None: run_statuses.append(
            (run_id, status, error)
        ),
    )
    monkeypatch.setattr(
        route_extraction, "update_session_status", lambda *args: None
    )
    monkeypatch.setattr(
        route_extraction,
        "_notify_extraction_run_completed",
        lambda *args: None,
    )

    try:
        asyncio.run(
            route_extraction._run_extraction_job(
                session_id=22,
                run_id=33,
                user="test-user",
                role="ANALYST",
                search_request_id=11,
            )
        )
    finally:
        logger.remove(handler_id)

    message = output.getvalue()
    assert "search_request_id=11" in message
    assert "session_id=22" in message
    assert "run_id=33" in message
    assert "RuntimeError" in message
    assert "provider initialization failed" in message
    assert "Traceback" in message
    assert run_statuses[-1][1] == "failed"


def test_missing_report_logs_case_failure_without_report_content(monkeypatch):
    db = SimpleNamespace(close=lambda: None)
    queue_item = SimpleNamespace(
        CaseId=44,
        ExtractionQueueId=55,
        AttemptCount=0,
        Status="pending",
    )
    queue_updates = []
    output, handler_id = _capture_logs()

    class FakeLlmClient:
        async def extract(self, report_text, schema):
            raise AssertionError("LLM must not run without report text")

    monkeypatch.setattr(route_extraction, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        route_extraction, "update_run_status", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        route_extraction, "update_session_status", lambda *args: None
    )
    monkeypatch.setattr(route_extraction, "get_llm_client", FakeLlmClient)
    monkeypatch.setattr(
        route_extraction, "get_queue", lambda *args: [queue_item]
    )
    monkeypatch.setattr(
        route_extraction,
        "get_run",
        lambda *args: SimpleNamespace(
            SchemaJson='{"diagnosis": {}}',
            LlmProvider="test-provider",
            LlmModel="test-model",
        ),
    )
    monkeypatch.setattr(
        route_extraction,
        "get_session",
        lambda *args: SimpleNamespace(TextSources=None),
    )
    monkeypatch.setattr(
        route_extraction, "parse_text_sources", lambda value: set()
    )
    monkeypatch.setattr(
        route_extraction, "reset_queue_statuses", lambda *args: None
    )
    monkeypatch.setattr(
        route_extraction,
        "is_run_cancellation_requested",
        lambda *args: False,
    )
    monkeypatch.setattr(
        route_extraction,
        "get_case_text_for_extraction",
        lambda *args, **kwargs: ("", []),
    )
    monkeypatch.setattr(
        route_extraction,
        "update_queue_item_status",
        lambda queue_id, status, db, error=None: queue_updates.append(
            (queue_id, status, error)
        ),
    )
    monkeypatch.setattr(
        route_extraction,
        "get_extraction_status",
        lambda *args: {
            "completed": 0,
            "failed": 1,
            "pending": 0,
            "running": 0,
        },
    )
    monkeypatch.setattr(
        route_extraction,
        "_notify_extraction_run_completed",
        lambda *args: None,
    )

    try:
        asyncio.run(
            route_extraction._run_extraction_job(
                session_id=22,
                run_id=33,
                user="test-user",
                role="ANALYST",
                search_request_id=11,
            )
        )
    finally:
        logger.remove(handler_id)

    message = output.getvalue()
    assert "reason=no_report_text" in message
    assert "search_request_id=11" in message
    assert "session_id=22" in message
    assert "run_id=33" in message
    assert "case_id=44" in message
    assert "report text" not in message
    assert queue_updates == [
        (55, "running", None),
        (55, "failed", "No report text found for this case"),
    ]


def test_case_exception_logs_traceback_and_request_context(monkeypatch):
    db = SimpleNamespace(close=lambda: None)
    queue_item = SimpleNamespace(
        CaseId=44,
        ExtractionQueueId=55,
        AttemptCount=0,
        Status="pending",
    )
    queue_updates = []
    output, handler_id = _capture_logs()

    class FakeLlmClient:
        async def extract(self, report_text, schema):
            raise ValueError("synthetic provider response error")

    monkeypatch.setattr(route_extraction, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        route_extraction, "update_run_status", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        route_extraction, "update_session_status", lambda *args: None
    )
    monkeypatch.setattr(route_extraction, "get_llm_client", FakeLlmClient)
    monkeypatch.setattr(
        route_extraction, "get_queue", lambda *args: [queue_item]
    )
    monkeypatch.setattr(
        route_extraction,
        "get_run",
        lambda *args: SimpleNamespace(
            SchemaJson='{"diagnosis": {}}',
            LlmProvider="test-provider",
            LlmModel="test-model",
        ),
    )
    monkeypatch.setattr(
        route_extraction,
        "get_session",
        lambda *args: SimpleNamespace(TextSources=None),
    )
    monkeypatch.setattr(
        route_extraction, "parse_text_sources", lambda value: set()
    )
    monkeypatch.setattr(
        route_extraction, "reset_queue_statuses", lambda *args: None
    )
    monkeypatch.setattr(
        route_extraction,
        "is_run_cancellation_requested",
        lambda *args: False,
    )
    monkeypatch.setattr(
        route_extraction,
        "get_case_text_for_extraction",
        lambda *args, **kwargs: ("synthetic report content", []),
    )
    monkeypatch.setattr(
        route_extraction,
        "update_queue_item_status",
        lambda queue_id, status, db, error=None: queue_updates.append(
            (queue_id, status, error)
        ),
    )
    monkeypatch.setattr(
        route_extraction,
        "get_extraction_status",
        lambda *args: {
            "completed": 0,
            "failed": 1,
            "pending": 0,
            "running": 0,
        },
    )
    monkeypatch.setattr(
        route_extraction,
        "_notify_extraction_run_completed",
        lambda *args: None,
    )

    try:
        asyncio.run(
            route_extraction._run_extraction_job(
                session_id=22,
                run_id=33,
                user="test-user",
                role="ANALYST",
                search_request_id=11,
            )
        )
    finally:
        logger.remove(handler_id)

    message = output.getvalue()
    assert "search_request_id=11" in message
    assert "session_id=22" in message
    assert "run_id=33" in message
    assert "case_id=44" in message
    assert "ValueError" in message
    assert "synthetic provider response error" in message
    assert "Traceback" in message
    assert "synthetic report content" not in message
    assert queue_updates[-1][1] == "failed"
