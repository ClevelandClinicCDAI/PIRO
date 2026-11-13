import asyncio
import re
from io import StringIO
from types import SimpleNamespace

import pytest

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


@pytest.mark.parametrize(
    "report_text,case_count",
    [
        ("", 1),
        ("synthetic report content", 1),
        ("synthetic report content", 11),
    ],
)
def test_case_progress_without_report_content(
    monkeypatch, report_text, case_count
):
    db = SimpleNamespace(close=lambda: None)
    queue_updates = []
    persisted_results = []
    output, handler_id = _capture_logs()
    queue = [
        SimpleNamespace(
            CaseId=44 + index,
            ExtractionQueueId=55 + index,
            AttemptCount=0,
            Status="pending",
        )
        for index in range(case_count)
    ]

    class FakeLlmClient:
        async def extract(self, report_text, schema):
            assert report_text
            return {
                "diagnosis": SimpleNamespace(
                    value="sensitive extracted value",
                    confidence=0.8,
                    provenance="sensitive provenance",
                )
            }

    monkeypatch.setattr(route_extraction, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        route_extraction, "update_run_status", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        route_extraction, "update_session_status", lambda *args: None
    )
    monkeypatch.setattr(route_extraction, "get_llm_client", FakeLlmClient)
    monkeypatch.setattr(route_extraction, "get_queue", lambda *args: queue)
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
        lambda *args, **kwargs: (report_text, []),
    )
    monkeypatch.setattr(
        route_extraction,
        "upsert_result",
        lambda **kwargs: persisted_results.append(kwargs["case_id"]),
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
            "completed": case_count if report_text else 0,
            "failed": 0 if report_text else case_count,
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
    assert "synthetic report content" not in message
    assert "sensitive extracted value" not in message
    assert "sensitive provenance" not in message
    assert "Extraction case started:" in message
    assert "Extraction case finished:" in message
    assert "elapsed_ms=" in message
    elapsed_values = re.findall(r"elapsed_ms=(\d+\.\d{2})", message)
    assert elapsed_values
    assert all(float(value) >= 0 for value in elapsed_values)
    assert f"processed={case_count} total={case_count}" in message
    if report_text:
        assert persisted_results == [item.CaseId for item in queue]
        for item in queue:
            case_logs = [
                line
                for line in message.splitlines()
                if f"case_id={item.CaseId} " in line
            ]
            phases = ["report_retrieval", "llm_call", "result_persistence"]
            assert len(case_logs) == 7
            for index, phase in enumerate(phases):
                assert f"phase={phase}" in case_logs[index * 2]
                assert "phase started:" in case_logs[index * 2]
                assert f"phase={phase} status=completed elapsed_ms=" in (
                    case_logs[index * 2 + 1]
                )
            assert "status=completed elapsed_ms=" in case_logs[-1]
        if case_count == 11:
            assert "processed=10 total=11 completed=10 failed=0" in message
            assert "processed=11 total=11 completed=11 failed=0" in message
    else:
        assert "reason=no_report_text" in message
        assert "phase=llm_call" not in message
        assert "status=failed elapsed_ms=" in message
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
    assert "phase=llm_call status=failed elapsed_ms=" in message
    assert "phase=result_persistence" not in message
    assert "processed=1 total=1 completed=0 failed=1" in message
