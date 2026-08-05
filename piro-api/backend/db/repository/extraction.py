"""Repository layer for the PIRO Extraction Suite."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionResult import ExtractionResult
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.views.VCaseCommentText import VCaseCommentText
from logger import logger

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
_TEXT_SOURCE_ORDER = {src["code"]: i for i, src in enumerate(AVAILABLE_TEXT_SOURCES)}

# Default set used when a session has no TextSources configured (backward
# compatible with sessions created before this feature existed).
DEFAULT_TEXT_SOURCES = {"final", "comment", "addendum", "microscopic"}

# Retained for backward compatibility with any external references.
_EXTRACTION_SHORT_NAMES = DEFAULT_TEXT_SOURCES

# Regex to strip the Cleveland Clinic LDT disclaimer boilerplate from report text.
# Uses flexible whitespace matching to handle formatting variations.
_LDT_DISCLAIMER_RE = re.compile(
    r"Laboratory\s+Developed\s+Test\s*\(LDT\)\s+Disclaimer\s*:.*?"
    r"Positive\s+and\s+negative\s+controls\s+stain\s+appropriately\s*\.",
    re.IGNORECASE | re.DOTALL,
)

def parse_text_sources(text_sources: Optional[str]) -> set:
    """Parse a session's stored comma-separated TextSources into a lowercase set.

    Falls back to DEFAULT_TEXT_SOURCES when unset/empty.
    """
    if not text_sources:
        return set(DEFAULT_TEXT_SOURCES)
    codes = {c.strip().lower() for c in text_sources.split(",") if c.strip()}
    return codes or set(DEFAULT_TEXT_SOURCES)


def serialize_text_sources(text_sources: Optional[List[str]]) -> Optional[str]:
    """Normalize a list of text source codes into the stored comma-separated form."""
    if text_sources is None:
        return None
    codes = [c.strip().lower() for c in text_sources if c and c.strip()]
    return ",".join(codes) if codes else None


def _segment_order(short_name: str) -> int:
    """Map a CommentType ShortName to a display-order index."""
    c = (short_name or "").lower()
    if "addend" in c:   # matches Addendum, Addend, etc.
        return _TEXT_SOURCE_ORDER.get("addendum", 99)
    return _TEXT_SOURCE_ORDER.get(c, 99)


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


def update_session_status(session_id: int, status: str, db: Session) -> None:
    session = get_session(session_id, db)
    if session:
        session.Status = status
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
    db.commit()
    db.refresh(run)
    return run


def get_run(run_id: int, db: Session) -> Optional[ExtractionRun]:
    return db.query(ExtractionRun).filter(ExtractionRun.ExtractionRunId == run_id).first()


def get_latest_run(session_id: int, db: Session) -> Optional[ExtractionRun]:
    return (
        db.query(ExtractionRun)
        .filter(ExtractionRun.ExtractionSessionId == session_id)
        .order_by(ExtractionRun.CreateDate.desc())
        .first()
    )


def update_run_status(
    run_id: int,
    status: str,
    db: Session,
    error: Optional[str] = None,
) -> None:
    run = get_run(run_id, db)
    if run is None:
        return
    run.Status = status
    if status == "running":
        run.StartedAt = datetime.now(timezone.utc)
    elif status in ("completed", "failed", "completed_with_errors"):
        run.CompletedAt = datetime.now(timezone.utc)
    if error:
        run.ErrorMessage = error
    db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# Queue CRUD
# ──────────────────────────────────────────────────────────────────────────────

def add_cases_to_queue(
    session_id: int, case_ids: List[int], user: str, db: Session
) -> List[ExtractionQueue]:
    added = []
    for case_id in case_ids:
        existing = (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.CaseId == case_id,
            )
            .first()
        )
        if existing is None:
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
    return (
        db.query(ExtractionQueue)
        .options(joinedload(ExtractionQueue.Case))
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .order_by(ExtractionQueue.CreateDate)
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


def update_queue_item_status(
    queue_item_id: int,
    status: str,
    db: Session,
    error: Optional[str] = None,
) -> None:
    item = db.query(ExtractionQueue).filter(
        ExtractionQueue.ExtractionQueueId == queue_item_id
    ).first()
    if item is None:
        return
    item.Status = status
    if error:
        item.ErrorMessage = error[:1000]
    if status == "running":
        item.AttemptCount = (item.AttemptCount or 0) + 1
    db.commit()


def reset_queue_statuses(session_id: int, db: Session) -> None:
    """Reset all queue items to 'pending' before a full run."""
    db.query(ExtractionQueue).filter(
        ExtractionQueue.ExtractionSessionId == session_id
    ).update({"Status": "pending", "ErrorMessage": None}, synchronize_session=False)
    db.commit()


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
) -> ExtractionResult:
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
        existing.ExtractedValue = extracted_value
        existing.Confidence = confidence
        existing.ProvenanceText = provenance_text
        existing.SourceCommentId = source_comment_id
        existing.ProvenanceStart = provenance_start
        existing.ProvenanceEnd = provenance_end
        existing.UpdateBy = user
        db.commit()
        db.refresh(existing)
        return existing

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
        IsReviewed=False,
        CreateBy=user,
        UpdateBy=user,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_results_for_session(session_id: int, db: Session) -> List[ExtractionResult]:
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
    """Return results for a specific run (rather than always the latest one)."""
    return (
        db.query(ExtractionResult)
        .options(joinedload(ExtractionResult.Case))
        .filter(ExtractionResult.ExtractionRunId == run_id)
        .order_by(ExtractionResult.CaseId, ExtractionResult.FieldName)
        .all()
    )


def get_incorrect_case_ids(session_id: int, db: Session) -> List[int]:
    """Return distinct case IDs from the latest run that have any field marked incorrect."""
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


def get_result_by_id(result_id: int, db: Session) -> Optional[ExtractionResult]:
    return db.query(ExtractionResult).filter(
        ExtractionResult.ExtractionResultId == result_id
    ).first()


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
    """Approve all un-reviewed results with confidence >= threshold. Returns count."""
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

def get_case_text_segments(
    case_id: int, db: Session, comment_types: Optional[set] = None
) -> List[VCaseCommentText]:
    """Fetch comment segments for extraction-relevant types in display order.

    Filters on V_CaseCommentText.CommentType (the ShortName already in the view)
    to avoid a redundant re-join to the CommentType table.
    ``comment_types`` is a lowercase set of codes (see AVAILABLE_TEXT_SOURCES);
    defaults to DEFAULT_TEXT_SOURCES (Final, Comment, Addendum, Microscopic)
    when not provided.
    Falls back to all available comment types if none of those are present.
    """
    types = comment_types if comment_types else DEFAULT_TEXT_SOURCES

    filters = [func.lower(VCaseCommentText.CommentType).in_(types)]
    if "addendum" in types:
        filters.append(func.lower(VCaseCommentText.CommentType).like('%addend%'))

    rows = (
        db.query(VCaseCommentText)
        .filter(VCaseCommentText.CaseId == case_id)
        .filter(or_(*filters))
        .all()
    )

    if not rows:
        # Fallback: use all comment types for this case and log what was found
        all_rows = (
            db.query(VCaseCommentText)
            .filter(VCaseCommentText.CaseId == case_id)
            .all()
        )
        available = [r.CommentType for r in all_rows]
        logger.warning(
            f"Case {case_id}: no segments matched selected extraction types "
            f"(available: {available}). Using all available comment text."
        )
        rows = all_rows

    rows.sort(key=lambda r: _segment_order(r.CommentType))
    return rows


def _strip_ldt_disclaimer(text: str) -> str:
    """Remove the Cleveland Clinic LDT disclaimer boilerplate from report text."""
    if not text:
        return text
    cleaned = _LDT_DISCLAIMER_RE.sub("", text)
    return cleaned.strip()


def build_labelled_report_text(segments: List[VCaseCommentText]) -> str:
    """Build a structured, labelled text string from comment segments.

    The LDT disclaimer boilerplate is stripped from each segment before assembly
    so it is neither displayed to users nor sent to the LLM.

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
) -> tuple[str, List[VCaseCommentText]]:
    """Return (labelled_text, segments) for LLM input.

    Applies DEMOADMIN masking if role == 'DEMOADMIN'.
    """
    segments = get_case_text_segments(case_id, db, comment_types=comment_types)

    # Apply PHI masking for demo mode (reuses existing SecurityUtil logic)
    if role and role.upper() == "DEMOADMIN":
        from core.security_util import SecurityUtil
        for seg in segments:
            seg.CommentText = SecurityUtil.mask_date(seg.CommentText)
            seg.CommentText = SecurityUtil.mask_case(seg.CommentText)

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
        }

    # For validation runs, scope progress to the run itself so the counter
    # reflects the validation set size, not the full queue.
    if latest_run.RunType == "validation" and latest_run.ValidationSize:
        total = latest_run.ValidationSize
        completed = (
            db.query(ExtractionResult.CaseId)
            .filter(ExtractionResult.ExtractionRunId == latest_run.ExtractionRunId)
            .distinct()
            .count()
        )
        failed = max(0, total - completed) if latest_run.Status in ("completed", "completed_with_errors", "failed") else (
            db.query(ExtractionQueue)
            .filter(
                ExtractionQueue.ExtractionSessionId == session_id,
                ExtractionQueue.Status == "failed",
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

    return {
        "session_id": session_id,
        "run_id": latest_run.ExtractionRunId,
        "status": latest_run.Status,
        "total": total,
        "completed": completed,
        "failed": failed,
    }
