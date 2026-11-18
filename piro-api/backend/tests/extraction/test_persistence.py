import asyncio
from datetime import datetime, timedelta, timezone
from io import StringIO
from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from apis.version1 import route_extraction
from db.models.Case import Case
from db.models.CaseComment import CaseComment
from db.models.CaseCommentSynopticSpecimen import CaseCommentSynopticSpecimen
from db.models.CommentType import CommentType
from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionResult import ExtractionResult
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.models.User import User
from db.repository import extraction
from db.views.VCaseCommentText import VCaseCommentText
from piro_logger import logger
from viewmodel.extraction import ExtractionRetryFailedRequest


@pytest.fixture
def state(db, monkeypatch):
    db.add(
        User(
            UserId=1,
            NUID="pytest",
            FirstName="Test",
            LastName="User",
            IsActive=True,
            CreateBy="pytest",
        )
    )
    db.add(
        CommentType(
            CommentTypeId=1,
            ShortName="final",
            Code="final",
            Description="Test",
            DataLabReference="test",
            ETLSource="test",
            IsActive=True,
            CreateBy="pytest",
        )
    )
    for case_id in (101, 102, 103):
        db.add(
            Case(
                CaseId=case_id,
                PatientId=1,
                HospitalId=1,
                CaseStatusId=1,
                CaseTypeId=1,
                SpecialtyId=1,
                SpecimenYear=2026,
                CaseNumber=f"TEST-{case_id}",
                AccessionDate=datetime(2026, 1, 1),
                IsActive=True,
                CreateBy="pytest",
            )
        )
    db.commit()
    session = extraction.create_session("Test", 1, "pytest", db)
    session_id = session.ExtractionSessionId
    extraction.update_session_schema(session_id, '{"grade": {}}', "pytest", db)
    run = extraction.create_run(
        session_id, '{"grade": {}}', "test", "test", "pytest", db
    )
    run_id = run.ExtractionRunId
    extraction.add_cases_to_queue(session_id, [101, 102, 103], "pytest", db)
    monkeypatch.setattr(route_extraction, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        route_extraction,
        "_notify_extraction_run_completed",
        lambda *args: None,
    )
    return SimpleNamespace(db=db, session_id=session_id, run_id=run_id)


def comment(state, text, comment_type="final", comment_id=501, case_id=101):
    db = state.db
    db.add(
        CaseComment(
            CaseCommentId=comment_id,
            CaseId=case_id,
            CommentTypeId=1,
            Text=text,
            IsActive=True,
            CreateBy="pytest",
        )
    )
    db.flush()
    db.add(
        VCaseCommentText(
            Id=comment_id,
            CaseId=case_id,
            CommentTypeId=1,
            CommentType=comment_type,
            CommentText=text,
            SourceCommentType=comment_type,
        )
    )
    db.commit()


def field(provenance="Grade: 2"):
    return SimpleNamespace(value="2", confidence=0.9, provenance=provenance)


def run_job(state, monkeypatch, fields=None, **kwargs):
    class Llm:
        async def extract(self, text, schema):
            return fields or {"grade": field()}

    monkeypatch.setattr(route_extraction, "get_llm_client", Llm)
    asyncio.run(
        route_extraction._run_extraction_job_async(
            state.session_id,
            state.run_id,
            "pytest",
            "ANALYST",
            **kwargs,
        )
    )


def stored_result(db, run_id, case_id=101, field_name="grade"):
    return (
        db.query(ExtractionResult)
        .filter_by(
            ExtractionRunId=run_id,
            CaseId=case_id,
            FieldName=field_name,
        )
        .one()
    )


@pytest.mark.parametrize(
    "source", ["final", "legacy_synoptic", "parsed_synoptic"]
)
def test_real_and_synoptic_provenance_with_foreign_keys(
    state, monkeypatch, source
):
    db = state.db
    text_sources = ["final"] if source == "final" else ["synoptic"]
    extraction.update_session_text_sources(
        state.session_id, text_sources, "pytest", db
    )
    if source == "parsed_synoptic":
        db.add(
            CaseCommentSynopticSpecimen(
                CaseId=101,
                SpecimenId=1,
                SynopticId=11,
                SynopticLine=1,
                CaseNum="TEST-101",
                SpecimenNum="A",
                RefSpecimenKey="1",
                RefRequisitionKey="1",
                CreateBy="pytest",
            )
        )
        db.commit()
        monkeypatch.setattr(
            extraction,
            "synoptic_report",
            lambda **kwargs: [
                SimpleNamespace(Key="Grade", Value="2"),
            ],
        )
    else:
        comment(
            state, "Grade: 2", "final" if source == "final" else "Synoptic"
        )

    run_job(state, monkeypatch, case_ids=[101])
    result = stored_result(db, state.run_id)
    assert result.SourceCommentId == (
        None if source == "parsed_synoptic" else 501
    )
    assert result.ProvenanceText == "Grade: 2"
    text, segments = extraction.get_case_text_for_extraction(
        101,
        db,
        comment_types=set(text_sources),
    )
    assert (
        text[result.ProvenanceStart : result.ProvenanceEnd]
        == result.ProvenanceText
    )
    assert "Grade: 2" in segments[0].CommentText
    # The review endpoint receives the same normalized text for quote matching.
    monkeypatch.setattr(
        route_extraction,
        "_require_session_read_access",
        lambda *args: extraction.get_session(state.session_id, db),
    )
    response = asyncio.run(
        route_extraction.get_case_text(
            101,
            1,
            "ANALYST",
            db,
            session_id=state.session_id,
        )
    )
    assert response.full_text == text
    assert response.segments[0].CommentText == segments[0].CommentText


def test_normalized_offsets_and_demo_text_do_not_modify_view_rows(
    state, monkeypatch
):
    disclaimer = (
        "Laboratory Developed Test (LDT) Disclaimer: synthetic boilerplate. "
        "Positive and negative controls stain appropriately."
    )
    comment(state, f"  {disclaimer}  ", comment_id=500)
    comment(state, f"  {disclaimer}\nDiagnosis: benign  ", comment_id=501)
    comment(state, "  Grade: 2  ", "comment", comment_id=502)
    run_job(state, monkeypatch, case_ids=[101])
    result = stored_result(state.db, state.run_id)
    text, segments = extraction.get_case_text_for_extraction(101, state.db)
    assert len(segments) == 2
    assert disclaimer not in text
    assert text[result.ProvenanceStart : result.ProvenanceEnd] == "Grade: 2"
    monkeypatch.setattr(
        extraction.SecurityUtil, "mask_date", lambda text: "MASK " + text
    )
    extraction.get_case_text_for_extraction(101, state.db, role="DEMOADMIN")
    state.db.commit()
    assert state.db.get(VCaseCommentText, 501).CommentText.startswith(
        "  Laboratory"
    )


def test_fk_failure_rolls_back_whole_case_and_continues(state, monkeypatch):
    comment(state, "Grade: 2")
    comment(state, "Grade: 2", comment_id=502, case_id=102)
    original = route_extraction.upsert_result
    related = extraction.create_run(
        state.session_id, "{}", "test", "test", "pytest", state.db
    )
    related_id = related.ExtractionRunId

    def fail_second_field(**kwargs):
        if kwargs["case_id"] == 101 and kwargs["field_name"] == "second":
            kwargs["source_comment_id"] = 999999
        return original(**kwargs)

    monkeypatch.setattr(route_extraction, "upsert_result", fail_second_field)
    logs = StringIO()
    handler = logger.add(logs, format="{message}\n{exception}", diagnose=False)
    try:
        run_job(
            state,
            monkeypatch,
            fields={"first": field(), "second": field()},
            case_ids=[101, 102],
            related_run_id=related_id,
        )
    finally:
        logger.remove(handler)
    assert "exception_type=IntegrityError" in logs.getvalue()
    assert "case_id=101" in logs.getvalue()
    assert "PendingRollbackError" not in logs.getvalue()
    db = state.db
    assert db.query(ExtractionResult).filter_by(CaseId=101).count() == 0
    assert db.query(ExtractionResult).filter_by(CaseId=102).count() == 4
    assert (
        db.query(ExtractionQueue).filter_by(CaseId=101).one().Status
        == "failed"
    )
    assert (
        db.query(ExtractionQueue).filter_by(CaseId=102).one().Status
        == "completed"
    )
    assert (
        db.get(ExtractionRun, state.run_id).Status == "completed_with_errors"
    )
    assert (
        db.get(ExtractionSession, state.session_id).Status
        == "completed_with_errors"
    )


def test_existing_review_and_related_results_survive_case_rollback(
    state, monkeypatch
):
    comment(state, "Grade: 2")
    related = extraction.create_run(
        state.session_id, "{}", "test", "test", "pytest", state.db
    )
    related_id = related.ExtractionRunId
    for run_id in (state.run_id, related_id):
        extraction.upsert_result(
            run_id,
            state.session_id,
            101,
            "first",
            '"old"',
            0.5,
            "Grade: 2",
            501,
            0,
            8,
            "pytest",
            state.db,
            reviewed_value='"reviewed"',
            is_reviewed=True,
            reviewed_by="reviewer",
        )
    original = route_extraction.upsert_result

    def fail_second_field(**kwargs):
        if kwargs["field_name"] == "second":
            kwargs["source_comment_id"] = 999999
        return original(**kwargs)

    monkeypatch.setattr(route_extraction, "upsert_result", fail_second_field)
    run_job(
        state,
        monkeypatch,
        fields={"first": field(), "second": field()},
        case_ids=[101],
        related_run_id=related_id,
    )
    for run_id in (state.run_id, related_id):
        result = stored_result(state.db, run_id, field_name="first")
        assert result.ExtractedValue == '"old"'
        assert result.ReviewedValue == '"reviewed"'
        assert result.IsReviewed
        assert result.ReviewedBy == "reviewer"


def test_queue_completion_failure_rolls_back_results(state, monkeypatch):
    comment(state, "Grade: 2")
    original = route_extraction.update_queue_item_status

    def fail_completion(queue_id, status, db, **kwargs):
        if status == "completed":
            raise RuntimeError("synthetic completion failure")
        return original(queue_id, status, db, **kwargs)

    monkeypatch.setattr(
        route_extraction, "update_queue_item_status", fail_completion
    )
    run_job(state, monkeypatch, case_ids=[101])
    assert state.db.query(ExtractionResult).count() == 0
    assert (
        state.db.query(ExtractionQueue).filter_by(CaseId=101).one().Status
        == "failed"
    )


def test_outer_failure_rolls_back_failed_session_and_updates_run(
    state, monkeypatch
):
    def fail_after_flush():
        state.db.add(
            ExtractionResult(
                ExtractionRunId=state.run_id,
                ExtractionSessionId=state.session_id,
                CaseId=101,
                FieldName="broken",
                SourceCommentId=999999,
                CreateBy="pytest",
            )
        )
        state.db.flush()

    monkeypatch.setattr(route_extraction, "get_llm_client", fail_after_flush)
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
    assert (
        state.db.query(ExtractionQueue).filter_by(Status="failed").count() == 3
    )
    assert state.db.query(ExtractionResult).count() == 0


def test_invalid_related_run_is_atomic_even_with_default_commit(state):
    with pytest.raises(IntegrityError):
        extraction.upsert_result(
            state.run_id,
            state.session_id,
            101,
            "grade",
            '"2"',
            0.9,
            "Grade: 2",
            None,
            0,
            8,
            "pytest",
            state.db,
            related_run_ids=[999999],
        )
    state.db.rollback()
    assert state.db.query(ExtractionResult).count() == 0


def test_queue_snapshots_do_not_reload_after_commits(state):
    queue = extraction.get_queue_for_extraction(state.session_id, state.db)
    state.db.commit()
    statements = []

    def count_queries(
        connection, cursor, statement, parameters, context, many
    ):
        statements.append(statement)

    engine = state.db.get_bind()
    event.listen(engine, "before_cursor_execute", count_queries)
    try:
        assert [item.CaseId for item in queue] == [101, 102, 103]
        assert all(item.Status == "pending" for item in queue)
    finally:
        event.remove(engine, "before_cursor_execute", count_queries)
    assert statements == []


def test_full_run_reprocesses_previously_completed_cases(state, monkeypatch):
    comment(state, "Grade: 2")
    queue_id = (
        state.db.query(ExtractionQueue)
        .filter_by(CaseId=101)
        .one()
        .ExtractionQueueId
    )
    extraction.update_queue_item_status(queue_id, "completed", state.db)
    extraction.upsert_result(
        state.run_id,
        state.session_id,
        101,
        "grade",
        '"old"',
        0.5,
        "Grade: 2",
        501,
        None,
        None,
        "pytest",
        state.db,
    )
    run_job(state, monkeypatch)
    assert stored_result(state.db, state.run_id).ExtractedValue == '"2"'
    assert state.db.get(ExtractionQueue, queue_id).AttemptCount == 1


def make_stale(state, run_type="full"):
    old = datetime.now(timezone.utc) - timedelta(hours=1)
    run = state.db.get(ExtractionRun, state.run_id)
    run.RunType = run_type
    run.Status = "running"
    run.StartedAt = old
    run.CreateDate = old
    state.db.query(ExtractionQueue).update(
        {"UpdateDate": old}, synchronize_session=False
    )
    state.db.query(ExtractionQueue).filter_by(CaseId=101).update(
        {"Status": "running", "UpdateDate": old},
        synchronize_session=False,
    )
    state.db.query(ExtractionQueue).filter_by(CaseId=103).update(
        {"Status": "completed", "UpdateDate": old},
        synchronize_session=False,
    )
    state.db.commit()


@pytest.mark.parametrize("run_type", ["full", "retry", "validation"])
def test_stale_recovery_repairs_session_and_owned_queue(state, run_type):
    make_stale(state, run_type)
    extraction.reclaim_stale_run(state.session_id, state.db)
    assert state.db.get(ExtractionRun, state.run_id).Status == "failed"
    assert state.db.get(ExtractionSession, state.session_id).Status == "failed"
    queue = extraction.get_queue_for_extraction(state.session_id, state.db)
    assert [item.Status for item in queue] == [
        "failed",
        "pending" if run_type == "validation" else "failed",
        "completed",
    ]


def test_recent_run_is_not_reclaimed_using_older_queue_activity(state):
    old = datetime.now(timezone.utc) - timedelta(hours=1)
    state.db.query(ExtractionQueue).update(
        {"UpdateDate": old}, synchronize_session=False
    )
    state.db.commit()
    extraction.reclaim_stale_run(state.session_id, state.db)
    assert state.db.get(ExtractionRun, state.run_id).Status == "pending"


def test_retry_reclaims_stale_run_before_selecting_failed_cases(
    state, monkeypatch
):
    make_stale(state)
    monkeypatch.setattr(
        route_extraction,
        "_require_session_ownership",
        lambda *args: state.db.get(ExtractionSession, state.session_id),
    )
    tasks = BackgroundTasks()
    run = route_extraction.retry_failed_cases(
        ExtractionRetryFailedRequest(session_id=state.session_id),
        tasks,
        "pytest",
        1,
        "ANALYST",
        state.db,
    )
    assert run.RunType == "retry"
    assert tasks.tasks[0].kwargs["case_ids"] == [101, 102]
    assert tasks.tasks[0].kwargs["related_run_id"] == state.run_id


def test_retry_clone_failure_does_not_leave_pending_run(state, monkeypatch):
    state.db.query(ExtractionQueue).filter_by(CaseId=101).update(
        {"Status": "failed"}
    )
    extraction.update_run_status(
        state.run_id, "completed_with_errors", state.db
    )
    monkeypatch.setattr(
        route_extraction,
        "_require_session_ownership",
        lambda *args: state.db.get(ExtractionSession, state.session_id),
    )

    def fail_clone(*args, **kwargs):
        raise RuntimeError("synthetic clone failure")

    monkeypatch.setattr(route_extraction, "clone_results_for_run", fail_clone)
    with pytest.raises(RuntimeError, match="clone failure"):
        route_extraction.retry_failed_cases(
            ExtractionRetryFailedRequest(session_id=state.session_id),
            BackgroundTasks(),
            "pytest",
            1,
            "ANALYST",
            state.db,
        )
    assert state.db.query(ExtractionRun).count() == 1
    assert (
        state.db.get(ExtractionRun, state.run_id).Status
        == "completed_with_errors"
    )


def test_retry_clones_successful_reviewed_fields(state, monkeypatch):
    extraction.upsert_result(
        state.run_id,
        state.session_id,
        103,
        "grade",
        '"old"',
        0.9,
        "Grade: 2",
        None,
        None,
        None,
        "pytest",
        state.db,
        reviewed_value='"reviewed"',
        is_reviewed=True,
        reviewed_by="reviewer",
    )
    make_stale(state)
    monkeypatch.setattr(
        route_extraction,
        "_require_session_ownership",
        lambda *args: state.db.get(ExtractionSession, state.session_id),
    )
    run = route_extraction.retry_failed_cases(
        ExtractionRetryFailedRequest(session_id=state.session_id),
        BackgroundTasks(),
        "pytest",
        1,
        "ANALYST",
        state.db,
    )
    result = stored_result(state.db, run.ExtractionRunId, case_id=103)
    assert result.ExtractedValue == '"old"'
    assert result.ReviewedValue == '"reviewed"'
    assert result.IsReviewed
    assert result.ReviewedBy == "reviewer"
