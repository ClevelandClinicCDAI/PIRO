"""Repository layer for the PIRO Extraction Suite."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import or_, func, text
from sqlalchemy.orm import Session, joinedload

from core.security_util import SecurityUtil
from db.models.CaseCommentSynopticSpecimen import CaseCommentSynopticSpecimen
from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionResult import ExtractionResult
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.repository.caseCommentSynoptic import synoptic_report
from db.views.VCaseCommentText import VCaseCommentText
from piro_logger import logger

# All selectable text sources for the schema builder's checkbox UI, in the
# order they should appear in the assembled report text. Codes are matched
# case-insensitively against V_CaseCommentText.CommentType.
AVAILABLE_TEXT_SOURCES: List[dict] = [
    {"code": "final", "label": "Final Diagnosis"},
    {"code": "comment", "label": "Diagnostic Comment"},
    {"code": "addendum", "label": "Addendum"},
    {"code": "microscopic", "label": "Microscopic Description"},
    {"code": "gross", "label": "Gross Description"},
    {"code": "intraop", "label": "IntraOp"},
    {"code": "resident", "label": "Resident"},
    {"code": "synoptic", "label": "Synoptic"},
    {"code": "clinical", "label": "Clinical"},
]
_TEXT_SOURCE_ORDER = {
    src["code"]: i for i, src in enumerate(AVAILABLE_TEXT_SOURCES)
}

# Default set used when a session has no TextSources configured (backward
# compatible with sessions created before this feature existed).
DEFAULT_TEXT_SOURCES = {"final", "comment", "addendum", "microscopic"}

# Retained for backward compatibility with any external references.
_EXTRACTION_SHORT_NAMES = DEFAULT_TEXT_SOURCES

# Regex to strip the Cleveland Clinic LDT disclaimer boilerplate from report
# text. Uses flexible whitespace matching to handle formatting variations.
_LDT_DISCLAIMER_RE = re.compile(
    r"Laboratory\s+Developed\s+Test\s*\(LDT\)\s+Disclaimer\s*:.*?"
    r"Positive\s+and\s+negative\s+controls\s+stain\s+appropriately\s*\.",
    re.IGNORECASE | re.DOTALL,
)


def parse_text_sources(text_sources: Optional[str]) -> set:
    """Parse a session's stored comma-separated TextSources into a
    lowercase set."""
    if not text_sources:
        return set()
    codes = {c.strip().lower() for c in text_sources.split(",") if c.strip()}
    return codes


def serialize_text_sources(text_sources: Optional[List[str]]) -> Optional[str]:
    """
    Normalize a list of text source codes into the stored comma-separated form.
    """
    if text_sources is None:
        return None
    codes = [c.strip().lower() for c in text_sources if c and c.strip()]
    return ",".join(codes) if codes else None


def _segment_order(short_name: str) -> int:
    """Map a CommentType ShortName to a display-order index."""
    c = (short_name or "").lower()
    if "addend" in c:  # matches Addendum, Addend, etc.
        return _TEXT_SOURCE_ORDER.get("addendum", 99)
    return _TEXT_SOURCE_ORDER.get(c, 99)


@dataclass(frozen=True)
class CaseTextSegment:
    """Dataclass representing a case text segment.

    Id identifies a displayed segment. SourceCommentId identifies an actual
    CaseComment row and is None for assembled synoptic text.
    """

    Id: int
    CaseId: int
    CommentTypeId: int
    CommentType: str
    CommentText: str
    SourceCommentType: str
    SourceCommentId: Optional[int]


def _comment_segment(row: VCaseCommentText) -> CaseTextSegment:
    return CaseTextSegment(
        Id=row.Id,
        CaseId=row.CaseId,
        CommentTypeId=row.CommentTypeId,
        CommentType=row.CommentType,
        CommentText=row.CommentText,
        SourceCommentType=row.SourceCommentType,
        SourceCommentId=row.Id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Session CRUD
# ──────────────────────────────────────────────────────────────────────────────


def create_session(
    name: str,
    user_id: int,
    user: str,
    db: Session,
    text_sources: Optional[List[str]] = None,
) -> ExtractionSession:
    session = ExtractionSession(
        UserId=user_id,
        Name=name,
        TextSources=serialize_text_sources(text_sources),
        Status="draft",
        IsActive=True,
        CreateBy=user,
        UpdateBy=user,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(session_id: int, db: Session) -> Optional[ExtractionSession]:
    return (
        db.query(ExtractionSession)
        .filter(
            ExtractionSession.ExtractionSessionId == session_id,
            ExtractionSession.IsActive == True,  # noqa: E712
        )
        .first()
    )


def list_user_sessions(user_id: int, db: Session) -> List[ExtractionSession]:
    return (
        db.query(ExtractionSession)
        .filter(
            ExtractionSession.UserId == user_id,
            ExtractionSession.IsActive == True,  # noqa: E712
        )
        .order_by(ExtractionSession.CreateDate.desc())
        .all()
    )


def update_session_schema(
    session_id: int, schema_json: str, user: str, db: Session
) -> Optional[ExtractionSession]:
    session = get_session(session_id, db)
    if session is None:
        return None
    session.SchemaJson = schema_json
    session.UpdateBy = user
    db.commit()
    db.refresh(session)
    return session


def update_session_name(
    session_id: int, name: str, user: str, db: Session
) -> Optional[ExtractionSession]:
    session = get_session(session_id, db)
    if session is None:
        return None
    session.Name = name
    session.UpdateBy = user
    db.commit()
    db.refresh(session)
    return session


def update_session_text_sources(
    session_id: int, text_sources: List[str], user: str, db: Session
) -> Optional[ExtractionSession]:
    session = get_session(session_id, db)
    if session is None:
        return None
    session.TextSources = serialize_text_sources(text_sources)
    session.UpdateBy = user
    db.commit()
    db.refresh(session)
    return session


def update_session_status(
    session_id: int, status: str, db: Session, *, commit: bool = True
) -> None:
    session = get_session(session_id, db)
    if session:
        session.Status = status
        if commit:
            db.commit()


def delete_session(session_id: int, user: str, db: Session) -> bool:
    session = get_session(session_id, db)
    if session is None:
        return False
    session.IsActive = False
    session.UpdateBy = user
    db.commit()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Run CRUD
# ──────────────────────────────────────────────────────────────────────────────


def create_run(
    session_id: int,
    schema_json: str,
    llm_provider: str,
    llm_model: str,
    user: str,
    db: Session,
    run_type: str = "full",
    validation_size: Optional[int] = None,
    *,
    commit: bool = True,
) -> ExtractionRun:
    run = ExtractionRun(
        ExtractionSessionId=session_id,
        SchemaJson=schema_json,
        LlmProvider=llm_provider,
        LlmModel=llm_model,
        Status="pending",
        RunType=run_type,
        ValidationSize=validation_size,
        CreateBy=user,
    )
    db.add(run)
    db.flush()
    if commit:
        db.commit()
        db.refresh(run)
    return run


def get_run(run_id: int, db: Session) -> Optional[ExtractionRun]:
    return (
        db.query(ExtractionRun)
        .filter(ExtractionRun.ExtractionRunId == run_id)
        .first()
    )


def get_latest_run(session_id: int, db: Session) -> Optional[ExtractionRun]:
    # Admission is serialized by the session lock. Identity order remains
    # reliable when timestamps reflect a transaction begun before that lock.
    return (
        db.query(ExtractionRun)
        .populate_existing()
        .filter(ExtractionRun.ExtractionSessionId == session_id)
        .order_by(ExtractionRun.ExtractionRunId.desc())
        .first()
    )


# Inactivity is a warning, not proof that a worker has stopped. Explicit
# recovery must fence its writes before allowing another run to start.
STALE_RUN_THRESHOLD_MINUTES = 30


class ExtractionRunSuperseded(RuntimeError):
    """The worker no longer owns this session's extraction writes."""


def lock_extraction_session(session_id: int, db: Session) -> None:
    """Serialize run admission, recovery, and worker writes until commit.

    The lock must be held in the same transaction as the guarded writes.
    SQL Server ignores FOR UPDATE, so use its transaction-scoped lock hints.
    """
    if db.get_bind().dialect.name == "sqlite":
        connection = db.connection().connection.driver_connection
        if not connection.in_transaction:
            db.execute(text("BEGIN IMMEDIATE"))
    session_id_found = (
        db.query(ExtractionSession.ExtractionSessionId)
        .filter(ExtractionSession.ExtractionSessionId == session_id)
        .with_hint(ExtractionSession, "WITH (UPDLOCK, HOLDLOCK)", "mssql")
        .with_for_update()
        .scalar()
    )
    if session_id_found is None:
        raise ExtractionRunSuperseded("Extraction session no longer exists")


def require_run_ownership(
    session_id: int, run_id: int, db: Session, *, allow_cancelled: bool = False
) -> None:
    """Fence every worker write using fresh state under the session lock."""
    lock_extraction_session(session_id, db)
    latest = get_latest_run(session_id, db)
    statuses = (
        ("pending", "running", "cancelled")
        if allow_cancelled
        else ("pending", "running")
    )
    if (
        latest is None
        or latest.ExtractionRunId != run_id
        or latest.Status not in statuses
    ):
        raise ExtractionRunSuperseded(
            f"Extraction run {run_id} no longer owns session {session_id}"
        )


def is_run_stale(
    run: ExtractionRun, last_activity: Optional[datetime]
) -> bool:
    """Read-only inactivity detection; it does not revoke worker ownership."""
    if run.Status not in ("pending", "running"):
        return False
    activity_dates = [
        value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        for value in (last_activity, run.StartedAt, run.CreateDate)
        if value is not None
    ]
    if not activity_dates:
        return False
    reference = max(activity_dates)

    now = datetime.now(timezone.utc)
    return now - reference > timedelta(minutes=STALE_RUN_THRESHOLD_MINUTES)


def reclaim_stale_run(
    session_id: int, db: Session, *, commit: bool = True
) -> Optional[ExtractionRun]:
    """Explicitly fence an inactive run while serializing replacement starts.

    With commit=False, the caller must commit/rollback; keep this lock through
    replacement run creation. Polling must use is_run_stale instead.
    """
    lock_extraction_session(session_id, db)
    run = get_latest_run(session_id, db)
    last_activity = (
        db.query(func.max(ExtractionQueue.UpdateDate))
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .scalar()
    )
    if run is None or not is_run_stale(run, last_activity):
        if commit:
            db.commit()
        return run

    logger.warning(
        "Fencing inactive extraction run: session_id={} run_id={}",
        session_id,
        run.ExtractionRunId,
    )
    now = datetime.now(timezone.utc)
    run.CancellationRequested = True
    run.Status = "failed"
    run.CompletedAt = datetime.now(timezone.utc)
    note = (
        "[Recovered] Run had no progress for over "
        f"{STALE_RUN_THRESHOLD_MINUTES} minutes; its writes were fenced "
        "before releasing the session for another run."
    )
    run.ErrorMessage = (
        f"{run.ErrorMessage}\n{note}" if run.ErrorMessage else note
    )
    update_session_status(session_id, "failed", db, commit=False)
    # Full/retry runs must make unprocessed cases retryable as well. A
    # validation run owns only its sampled cases; leave other pending cases.
    unfinished = (
        ("running",) if run.RunType == "validation" else ("pending", "running")
    )
    db.query(ExtractionQueue).filter(
        ExtractionQueue.ExtractionSessionId == session_id,
        ExtractionQueue.Status.in_(unfinished),
    ).update(
        {"Status": "failed", "ErrorMessage": note, "UpdateDate": now},
        synchronize_session=False,
    )
    db.flush()
    if commit:
        db.commit()
        db.refresh(run)
    return run


def update_run_status(
    run_id: int,
    status: str,
    db: Session,
    error: Optional[str] = None,
    *,
    commit: bool = True,
) -> None:
    run = get_run(run_id, db)
    if run is None:
        return
    run.Status = status
    if status == "running":
        run.StartedAt = datetime.now(timezone.utc)
    elif status in (
        "completed",
        "failed",
        "completed_with_errors",
        "cancelled",
    ):
        run.CompletedAt = datetime.now(timezone.utc)
    if error:
        run.ErrorMessage = error
    if commit:
        db.commit()


def request_run_cancellation(
    run_id: int, db: Session
) -> Optional[ExtractionRun]:
    """Flag an in-progress run for cooperative cancellation.

    The background job checks ``is_run_cancellation_requested`` between
    cases and stops before starting the next one — it can't interrupt an
    in-flight LLM call, so at most one case finishes after this is called.
    Cases already completed keep their results; the rest stay queued so the
    run can be resumed later.
    """
    run = get_run(run_id, db)
    if run is None or run.Status not in ("pending", "running"):
        return run
    run.CancellationRequested = True
    db.commit()
    db.refresh(run)
    return run


def is_run_cancellation_requested(run_id: int, db: Session) -> bool:
    # Query a fresh row (bypassing the session identity-map cache) so the
    # background job's long-lived ORM objects see cancellation requests
    # made from a different request/DB session.
    flag = (
        db.query(ExtractionRun.CancellationRequested)
        .filter(ExtractionRun.ExtractionRunId == run_id)
        .scalar()
    )
    return bool(flag)


# ──────────────────────────────────────────────────────────────────────────────
# Queue CRUD
# ──────────────────────────────────────────────────────────────────────────────


def add_cases_to_queue(
    session_id: int, case_ids: List[int], user: str, db: Session
) -> List[ExtractionQueue]:
    """Bulk-add cases to a session's extraction queue.

    Fetches already-queued CaseIds in batches (avoids the SQL Server ~2100
    bound-parameter limit on IN clauses) instead of issuing one existence
    check query per case, which was the main bottleneck when loading large
    saved searches into the queue.
    """
    if not case_ids:
        return []

    # deduplicate case IDs while preserving order
    unique_case_ids: list = []
    for case_id in case_ids:
        if case_id not in unique_case_ids:
            unique_case_ids.append(case_id)
    existing_ids: set = set()
    CHUNK_SIZE = 1000
    for i in range(0, len(unique_case_ids), CHUNK_SIZE):
        chunk = unique_case_ids[i : i + CHUNK_SIZE]
        rows = (
            db.query(ExtractionQueue.CaseId)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.CaseId.in_(chunk),
            )
            .all()
        )
        existing_ids.update(row.CaseId for row in rows)

    added = []
    for case_id in unique_case_ids:
        if case_id in existing_ids:
            continue
        item = ExtractionQueue(
            ExtractionSessionId=session_id,
            CaseId=case_id,
            Status="pending",
            AttemptCount=0,
            CreateBy=user,
            UpdateBy=user,
        )
        db.add(item)
        added.append(item)
    db.commit()
    return added


def get_queue(session_id: int, db: Session) -> List[ExtractionQueue]:
    """Retrieve ExtractionQueue records for a session.

    Returns all values from the ExtractionQueue table, plus Case data."""

    return (
        db.query(ExtractionQueue)
        .options(joinedload(ExtractionQueue.Case))
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .order_by(ExtractionQueue.CreateDate)
        .all()
    )


def get_queue_for_extraction(session_id: int, db: Session) -> list:
    """Retrieve ExtractionQueue records for a session.

    Returns a more limited set of values than `get_queue`, including only key
    values needed for extraction."""

    return (
        db.query(
            ExtractionQueue.ExtractionQueueId,
            ExtractionQueue.CaseId,
            ExtractionQueue.Status,
            ExtractionQueue.AttemptCount,
        )
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .order_by(
            ExtractionQueue.CreateDate, ExtractionQueue.ExtractionQueueId
        )
        .all()
    )


def remove_from_queue(session_id: int, case_id: int, db: Session) -> bool:
    item = (
        db.query(ExtractionQueue)
        .filter(
            ExtractionQueue.ExtractionSessionId == session_id,
            ExtractionQueue.CaseId == case_id,
        )
        .first()
    )
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


def clear_queue(session_id: int, db: Session) -> int:
    """Remove every queued case for a session so a new case set can be loaded.

    Returns the number of items removed. Does not touch prior run results —
    those stay associated with the session's run history for export.
    """
    deleted = (
        db.query(ExtractionQueue)
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def update_queue_item_status(
    queue_item_id: int,
    status: str,
    db: Session,
    error: Optional[str] = None,
    *,
    commit: bool = True,
) -> None:
    item = (
        db.query(ExtractionQueue)
        .filter(ExtractionQueue.ExtractionQueueId == queue_item_id)
        .first()
    )
    if item is None:
        return
    item.Status = status
    if error:
        item.ErrorMessage = error[:1000]
    if status == "running":
        item.AttemptCount = (item.AttemptCount or 0) + 1
    # Set explicitly in Python (UTC-aware) rather than relying on the
    # column's onupdate=func.now(), which on MSSQL compiles to
    # CURRENT_TIMESTAMP — the DB server's naive local clock. That naive
    # value serializes over the API without a timezone suffix, so the
    # browser parses it as local browser time, not UTC. This can skew the
    # "last activity" heartbeat by hours and made actively-running jobs
    # falsely show as "Possibly stalled" in the UI. Using the same
    # datetime.now(timezone.utc) convention as StartedAt/CompletedAt keeps
    # all run/queue timestamps consistently UTC-aware.
    item.UpdateDate = datetime.now(timezone.utc)
    if commit:
        db.commit()


def reset_queue_statuses(session_id: int, db: Session) -> None:
    """Reset all queue items to 'pending' before a full run."""
    db.query(ExtractionQueue).filter(
        ExtractionQueue.ExtractionSessionId == session_id
    ).update(
        {"Status": "pending", "ErrorMessage": None}, synchronize_session=False
    )
    db.commit()


def fail_unfinished_queue(
    session_id: int,
    db: Session,
    error: str,
    case_ids: Optional[List[int]] = None,
) -> None:
    """Update per-case records in the ExtractionQueue table, setting status to
    Failed.

    This is needed when a run has been interrupted, so that we can retry cases.
    """
    chunks = (
        [None]
        if case_ids is None
        else [
            case_ids[index : index + 1000]
            for index in range(0, len(case_ids), 1000)
        ]
    )
    for chunk in chunks:
        query = db.query(ExtractionQueue).filter(
            ExtractionQueue.ExtractionSessionId == session_id,
            ExtractionQueue.Status.in_(("pending", "running")),
        )
        if chunk is not None:
            query = query.filter(ExtractionQueue.CaseId.in_(chunk))
        query.update(
            {
                "Status": "failed",
                "ErrorMessage": error[:1000],
                "UpdateDate": datetime.now(timezone.utc),
            },
            synchronize_session=False,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Result CRUD
# ──────────────────────────────────────────────────────────────────────────────


def upsert_result(
    run_id: int,
    session_id: int,
    case_id: int,
    field_name: str,
    extracted_value: Optional[str],
    confidence: Optional[float],
    provenance_text: Optional[str],
    source_comment_id: Optional[int],
    provenance_start: Optional[int],
    provenance_end: Optional[int],
    user: str,
    db: Session,
    reviewed_value: Optional[str] = None,
    is_reviewed: Optional[bool] = None,
    is_incorrect: Optional[bool] = None,
    reviewed_by: Optional[str] = None,
    reviewed_date: Optional[datetime] = None,
    related_run_ids: Optional[List[int]] = None,
    *,
    commit: bool = True,
) -> ExtractionResult:
    """Insert or update an extraction result for a given run, session, and
    case.

    If a result already exists for the specified run, session, case, and field,
    it will be updated with the provided values. Otherwise, a new result will
    be created.

    With commit=False, the caller owns the transaction for all fields and
    related-run writes. Flushing detects constraint failures without making
    partial results durable.
    """

    def _apply_result_values(result: ExtractionResult) -> ExtractionResult:
        """Apply the provided result values to the given ExtractionResult
        instance."""
        result.ExtractedValue = extracted_value
        result.Confidence = confidence
        result.ProvenanceText = provenance_text
        result.SourceCommentId = source_comment_id
        result.ProvenanceStart = provenance_start
        result.ProvenanceEnd = provenance_end
        result.ReviewedValue = reviewed_value
        if is_reviewed is not None:
            result.IsReviewed = is_reviewed
        if is_incorrect is not None:
            result.IsIncorrect = is_incorrect
        if reviewed_by is not None:
            result.ReviewedBy = reviewed_by
        if reviewed_date is not None:
            result.ReviewedDate = reviewed_date
        result.UpdateBy = user
        return result

    existing = (
        db.query(ExtractionResult)
        .filter(
            ExtractionResult.ExtractionRunId == run_id,
            ExtractionResult.CaseId == case_id,
            ExtractionResult.FieldName == field_name,
        )
        .first()
    )
    if existing:
        _apply_result_values(existing)
        result = existing
    else:
        result = ExtractionResult(
            ExtractionRunId=run_id,
            ExtractionSessionId=session_id,
            CaseId=case_id,
            FieldName=field_name,
            ExtractedValue=extracted_value,
            Confidence=confidence,
            ProvenanceText=provenance_text,
            SourceCommentId=source_comment_id,
            ProvenanceStart=provenance_start,
            ProvenanceEnd=provenance_end,
            ReviewedValue=reviewed_value,
            IsReviewed=is_reviewed if is_reviewed is not None else False,
            IsIncorrect=is_incorrect if is_incorrect is not None else False,
            ReviewedBy=reviewed_by,
            ReviewedDate=reviewed_date,
            CreateBy=user,
            UpdateBy=user,
        )
        db.add(result)
    db.flush()

    current_run_id = run_id

    # de-duplicate related run IDs
    deduplicated_related_run_ids = []
    if related_run_ids:
        for related_run_id in related_run_ids:
            if related_run_id not in deduplicated_related_run_ids:
                deduplicated_related_run_ids.append(related_run_id)

    # update related runs, ensuring that each related run has the same result
    # as the current run
    for related_run_id in deduplicated_related_run_ids:
        if related_run_id == current_run_id:
            continue

        existing_result_from_another_run = (
            db.query(ExtractionResult)
            .filter(
                ExtractionResult.ExtractionRunId == related_run_id,
                ExtractionResult.CaseId == case_id,
                ExtractionResult.FieldName == field_name,
            )
            .first()
        )

        if existing_result_from_another_run:
            _apply_result_values(existing_result_from_another_run)
            existing_result_from_another_run.ExtractionSessionId = session_id
        else:
            mirror_result = ExtractionResult(
                ExtractionRunId=related_run_id,
                ExtractionSessionId=session_id,
                CaseId=case_id,
                FieldName=field_name,
                ExtractedValue=extracted_value,
                Confidence=confidence,
                ProvenanceText=provenance_text,
                SourceCommentId=source_comment_id,
                ProvenanceStart=provenance_start,
                ProvenanceEnd=provenance_end,
                ReviewedValue=reviewed_value,
                IsReviewed=is_reviewed if is_reviewed is not None else False,
                IsIncorrect=(
                    is_incorrect if is_incorrect is not None else False
                ),
                ReviewedBy=reviewed_by,
                ReviewedDate=reviewed_date,
                CreateBy=user,
                UpdateBy=user,
            )
            db.add(mirror_result)
        db.flush()
    if commit:
        db.commit()
        db.refresh(result)
    return result


def clone_results_for_run(
    source_run_id: int,
    destination_run_id: int,
    user: str,
    db: Session,
    *,
    commit: bool = True,
) -> int:
    """Copy every result row from one run into another run.

    Retry runs use this to start with the successful rows from the preceding
    run so the latest session export stays complete while the retry is only
    filling in the previously failed cases.
    """
    results = get_results_for_run(source_run_id, db)
    copied = 0
    for result in results:
        upsert_result(
            run_id=destination_run_id,
            session_id=result.ExtractionSessionId,
            case_id=result.CaseId,
            field_name=result.FieldName,
            extracted_value=result.ExtractedValue,
            confidence=result.Confidence,
            provenance_text=result.ProvenanceText,
            source_comment_id=result.SourceCommentId,
            provenance_start=result.ProvenanceStart,
            provenance_end=result.ProvenanceEnd,
            reviewed_value=result.ReviewedValue,
            is_reviewed=result.IsReviewed,
            is_incorrect=result.IsIncorrect,
            reviewed_by=result.ReviewedBy,
            reviewed_date=result.ReviewedDate,
            user=user,
            db=db,
            commit=False,
        )
        copied += 1
    if commit:
        db.commit()
    return copied


def get_results_for_session(
    session_id: int, db: Session
) -> List[ExtractionResult]:
    """Return results from the latest run for a session."""
    latest_run = get_latest_run(session_id, db)
    if latest_run is None:
        return []
    return (
        db.query(ExtractionResult)
        .options(joinedload(ExtractionResult.Case))
        .filter(ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId)
        .order_by(ExtractionResult.CaseId, ExtractionResult.FieldName)
        .all()
    )


def get_results_for_run(run_id: int, db: Session) -> List[ExtractionResult]:
    """
    Return results for a specific run (rather than always the latest one).
    """
    return (
        db.query(ExtractionResult)
        .options(joinedload(ExtractionResult.Case))
        .filter(ExtractionResult.ExtractionRunId == run_id)
        .order_by(ExtractionResult.CaseId, ExtractionResult.FieldName)
        .all()
    )


def get_incorrect_case_ids(session_id: int, db: Session) -> List[int]:
    """Return distinct case IDs from the latest run that have any field marked
    incorrect."""
    latest_run = get_latest_run(session_id, db)
    if latest_run is None:
        return []
    rows = (
        db.query(ExtractionResult.CaseId)
        .filter(
            ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId,
            ExtractionResult.IsReviewed == True,  # noqa: E712
            ExtractionResult.IsIncorrect == True,  # noqa: E712
        )
        .distinct()
        .all()
    )
    return [r.CaseId for r in rows]


def get_failed_case_ids(session_id: int, db: Session) -> List[int]:
    """Return case IDs whose most recent queue attempt ended in 'failed'
    (e.g. a transient LLM provider error) so they can be resubmitted
    without reprocessing the rest of the session's queue."""
    rows = (
        db.query(ExtractionQueue.CaseId)
        .filter(
            ExtractionQueue.ExtractionSessionId == session_id,
            ExtractionQueue.Status == "failed",
        )
        .all()
    )
    return [r.CaseId for r in rows]


def get_low_confidence_case_ids(
    session_id: int, threshold: float, db: Session
) -> List[int]:
    """Return distinct case IDs from the latest run that have any field with
    confidence below threshold OR that are not yet reviewed."""
    latest_run = get_latest_run(session_id, db)
    if latest_run is None:
        return []
    rows = (
        db.query(ExtractionResult.CaseId)
        .filter(
            ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId,
            (ExtractionResult.Confidence < threshold)
            | (ExtractionResult.IsReviewed == False),  # noqa: E712
        )
        .distinct()
        .all()
    )
    return [r.CaseId for r in rows]


def get_result_by_id(
    result_id: int, db: Session
) -> Optional[ExtractionResult]:
    return (
        db.query(ExtractionResult)
        .filter(ExtractionResult.ExtractionResultId == result_id)
        .first()
    )


def update_result_review(
    result_id: int,
    reviewed_value: Optional[str],
    is_reviewed: Optional[bool],
    reviewer: str,
    db: Session,
    is_incorrect: Optional[bool] = None,
) -> Optional[ExtractionResult]:
    result = get_result_by_id(result_id, db)
    if result is None:
        return None
    if reviewed_value is not None:
        result.ReviewedValue = reviewed_value
    if is_reviewed is not None:
        result.IsReviewed = is_reviewed
        if is_reviewed:
            result.ReviewedBy = reviewer
            result.ReviewedDate = datetime.now(timezone.utc)
    if is_incorrect is not None:
        result.IsIncorrect = is_incorrect
    result.UpdateBy = reviewer
    db.commit()
    db.refresh(result)
    return result


def bulk_approve_high_confidence(
    session_id: int, threshold: float, reviewer: str, db: Session
) -> int:
    """Approve all un-reviewed results with confidence >= threshold. Returns
    count."""
    latest_run = get_latest_run(session_id, db)
    if latest_run is None:
        return 0
    results = (
        db.query(ExtractionResult)
        .filter(
            ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId,
            ExtractionResult.IsReviewed == False,  # noqa: E712
            ExtractionResult.Confidence >= threshold,
            ExtractionResult.ExtractedValue.isnot(None),
        )
        .all()
    )
    now = datetime.now(timezone.utc)
    for r in results:
        r.IsReviewed = True
        r.ReviewedBy = reviewer
        r.ReviewedDate = now
        r.UpdateBy = reviewer
    db.commit()
    return len(results)


# ──────────────────────────────────────────────────────────────────────────────
# Case text helpers
# ──────────────────────────────────────────────────────────────────────────────


def _build_synoptic_segment(
    case_id: int, db: Session
) -> Optional[CaseTextSegment]:
    """Build a synthetic 'Synoptic' text segment sourced from
    CaseCommentSynopticSpecimen / CaseCommentSynopticText — the same tables
    the case detail UI's synoptic report is built from — instead of
    CaseComment.

    CaseComment only reliably contains synoptic report text for cases from
    before ~2022; more recent cases store the parsed synoptic data in
    CaseCommentSynopticText instead. Sourcing from there matches how regular
    (non-extraction) data requests assemble synoptic text regardless of case
    age. Returns None if no parsed synoptic data exists for the case (e.g.
    older cases), letting the caller fall back to CaseComment.
    """
    synoptic_ids = [
        row[0]
        for row in (
            db.query(CaseCommentSynopticSpecimen.SynopticId)
            .filter(CaseCommentSynopticSpecimen.CaseId == case_id)
            .distinct()
            .order_by(CaseCommentSynopticSpecimen.SynopticId)
            .all()
        )
    ]
    if not synoptic_ids:
        return None

    lines: List[str] = []
    for synoptic_id in synoptic_ids:
        for row in synoptic_report(synopticId=synoptic_id, db=db):
            key = (row.Key or "").strip()
            value = (row.Value or "").strip()
            if not key and not value:
                continue
            lines.append(f"{key}: {value}" if key and value else key or value)

    text = "\n".join(lines).strip()
    if not text:
        return None

    return CaseTextSegment(
        Id=-case_id,
        CaseId=case_id,
        CommentTypeId=0,
        CommentType="Synoptic",
        CommentText=text,
        SourceCommentType="Synoptic",
        SourceCommentId=None,
    )


def get_case_text_segments(
    case_id: int, db: Session, comment_types: Optional[set] = None
) -> List[CaseTextSegment]:
    """Fetch comment segments for extraction-relevant types in display order.

    Filters on V_CaseCommentText.CommentType (the ShortName already in the
    view) to avoid a redundant re-join to the CommentType table.
    ``comment_types`` is a lowercase set of codes (see AVAILABLE_TEXT_SOURCES).

    The 'synoptic' source is handled separately: it is preferentially built
    from CaseCommentSynopticSpecimen/CaseCommentSynopticText (see
    ``_build_synoptic_segment``), since CaseComment does not reliably contain
    synoptic text for cases after ~2022. If no parsed synoptic data exists
    for the case (common for older cases), this falls back to the raw
    synoptic text in CaseComment/V_CaseCommentText.

    If the comment_types are explicitly specified (for example the user selects
    only 'gross'), and none of those sections exist on the case, return an
    empty list.

    If comment_types are not specified, default types are tried.  If no
    comments are found among the default types, the selection of comment types
    is expanded to include all types as a fallback."""

    types: set
    allow_all_comment_types_fallback: bool = False

    if comment_types:
        types = comment_types
    else:
        types = DEFAULT_TEXT_SOURCES
        allow_all_comment_types_fallback = True

    non_synoptic_types = types - {"synoptic"}

    rows: List[CaseTextSegment] = []
    if non_synoptic_types:
        filters = [
            func.lower(VCaseCommentText.CommentType).in_(non_synoptic_types)
        ]
        if "addendum" in non_synoptic_types:
            filters.append(
                func.lower(VCaseCommentText.CommentType).like("%addend%")
            )
        comment_rows = (
            db.query(VCaseCommentText)
            .filter(VCaseCommentText.CaseId == case_id)
            .filter(or_(*filters))
            .order_by(VCaseCommentText.Id)
            .all()
        )
        rows = [_comment_segment(row) for row in comment_rows]

    if "synoptic" in types:
        synoptic_segment = _build_synoptic_segment(case_id, db)
        if synoptic_segment is not None:
            rows.append(synoptic_segment)
        else:
            # Older cases (pre-~2022) often have no parsed
            # CaseCommentSynopticText data; fall back to whatever raw
            # synoptic text CaseComment has for the case, matching the
            # extraction suite's prior behavior for those cases.
            legacy_synoptic_rows = (
                db.query(VCaseCommentText)
                .filter(VCaseCommentText.CaseId == case_id)
                .filter(func.lower(VCaseCommentText.CommentType) == "synoptic")
                .order_by(VCaseCommentText.Id)
                .all()
            )
            rows.extend(_comment_segment(row) for row in legacy_synoptic_rows)

    if rows:
        rows.sort(key=lambda r: _segment_order(r.CommentType))
        return rows

    if allow_all_comment_types_fallback:
        all_rows = (
            db.query(VCaseCommentText)
            .filter(VCaseCommentText.CaseId == case_id)
            .order_by(VCaseCommentText.Id)
            .all()
        )
        available = [r.CommentType for r in all_rows]
        logger.warning(
            "Case %s: no segments matched selected extraction types "
            "(available: %s). Using all available comment text because "
            "fallback is enabled.",
            case_id,
            available,
        )
        all_rows.sort(key=lambda r: _segment_order(r.CommentType))
        return [_comment_segment(row) for row in all_rows]
    else:
        logger.info(
            "Case %s: no segments matched explicit text-source selection %s; "
            "returning no text to honor the configured scope.",
            case_id,
            sorted(types),
        )
        return []


def _strip_ldt_disclaimer(text: str) -> str:
    """
    Remove the Cleveland Clinic LDT disclaimer boilerplate from report text.
    """
    if not text:
        return text
    cleaned = _LDT_DISCLAIMER_RE.sub("", text)
    return cleaned.strip()


def build_labelled_report_text(segments: List[CaseTextSegment]) -> str:
    """Build a structured, labelled text string from comment segments.

    The LDT disclaimer boilerplate is stripped from each segment before
    assembly so it is neither displayed to users nor sent to the LLM.

    Example output:
        Final Diagnosis:
        Invasive ductal carcinoma, grade 2...

        Microscopic Description:
        Sections show...
    """
    parts = []
    for seg in segments:
        clean_text = _strip_ldt_disclaimer(seg.CommentText)
        if clean_text:
            parts.append(f"{seg.CommentType}:\n{clean_text}")
    return "\n\n".join(parts)


def get_case_text_for_extraction(
    case_id: int,
    db: Session,
    role: Optional[str] = None,
    comment_types: Optional[set] = None,
) -> tuple[str, List[CaseTextSegment]]:
    """Return (labelled_text, segments) for LLM input.

    Applies DEMOADMIN masking if role == 'DEMOADMIN'.
    """
    segments = get_case_text_segments(case_id, db, comment_types=comment_types)

    normalized = []
    for seg in segments:
        text = _strip_ldt_disclaimer(seg.CommentText)
        if role and role.upper() == "DEMOADMIN":
            text = SecurityUtil.mask_case(SecurityUtil.mask_date(text))
        if text:
            normalized.append(replace(seg, CommentText=text))
    segments = normalized

    labelled_text = build_labelled_report_text(segments)
    return labelled_text, segments


# ──────────────────────────────────────────────────────────────────────────────
# Progress / status helpers
# ──────────────────────────────────────────────────────────────────────────────


def get_extraction_status(session_id: int, db: Session) -> dict:
    """Return progress counts for the latest run of a session."""
    latest_run = get_latest_run(session_id, db)
    session = get_session(session_id, db)

    if latest_run is None:
        total = (
            db.query(ExtractionQueue)
            .filter(ExtractionQueue.ExtractionSessionId == session_id)
            .count()
        )
        return {
            "session_id": session_id,
            "run_id": None,
            "status": session.Status if session else "unknown",
            "total": total,
            "completed": 0,
            "failed": 0,
            "pending": total,
            "running": 0,
            "started_at": None,
            "completed_at": None,
            "last_updated_at": None,
            "is_stale": False,
        }

    # Most recent queue-item activity, used as a "still alive" heartbeat for
    # long-running jobs (a stalled/crashed run will stop advancing this).
    last_updated_at = (
        db.query(func.max(ExtractionQueue.UpdateDate))
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .scalar()
    )

    # For validation runs, scope progress to the run itself so the counter
    # reflects the validation set size, not the full queue.
    if latest_run.RunType == "validation" and latest_run.ValidationSize:
        total = latest_run.ValidationSize
        completed = (
            db.query(ExtractionResult.CaseId)
            .filter(
                ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId
            )
            .distinct()
            .count()
        )
        failed = (
            max(0, total - completed)
            if latest_run.Status
            in ("completed", "completed_with_errors", "failed")
            else (
                db.query(ExtractionQueue)
                .filter(
                    ExtractionQueue.ExtractionSessionId == session_id,
                    ExtractionQueue.Status == "failed",
                )
                .count()
            )
        )
        pending = max(0, total - completed - failed)
        running = (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.Status == "running",
            )
            .count()
        )
    else:
        total = (
            db.query(ExtractionQueue)
            .filter(ExtractionQueue.ExtractionSessionId == session_id)
            .count()
        )
        completed = (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.Status == "completed",
            )
            .count()
        )
        failed = (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.Status == "failed",
            )
            .count()
        )
        running = (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.Status == "running",
            )
            .count()
        )
        pending = max(0, total - completed - failed - running)

    return {
        "session_id": session_id,
        "run_id": latest_run.ExtractionRunId,
        "status": latest_run.Status,
        "total": total,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "running": running,
        "started_at": latest_run.StartedAt,
        "completed_at": latest_run.CompletedAt,
        "last_updated_at": last_updated_at,
        "is_stale": is_run_stale(latest_run, last_updated_at),
    }
