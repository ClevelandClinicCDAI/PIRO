"""Repository layer for the PIRO Extraction Suite."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from db.models.CommentType import CommentType as CommentTypeModel
from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionResult import ExtractionResult
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.views.VCaseCommentText import VCaseCommentText

# Comment types included in extraction, in the order they appear in the report.
_EXTRACTION_COMMENT_CODES = ["FINAL", "COMMENT", "ADDEND", "MICROSCOPIC"]
_EXTRACTION_CODE_ORDER = {code: i for i, code in enumerate(_EXTRACTION_COMMENT_CODES)}


# ──────────────────────────────────────────────────────────────────────────────
# Session CRUD
# ──────────────────────────────────────────────────────────────────────────────

def create_session(name: str, user_id: int, user: str, db: Session) -> ExtractionSession:
    session = ExtractionSession(
        UserId=user_id,
        Name=name,
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
) -> ExtractionRun:
    run = ExtractionRun(
        ExtractionSessionId=session_id,
        SchemaJson=schema_json,
        LlmProvider=llm_provider,
        LlmModel=llm_model,
        Status="pending",
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
    elif status in ("completed", "failed"):
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

def get_case_text_segments(case_id: int, db: Session) -> List[VCaseCommentText]:
    """Fetch comment segments for extraction-relevant types in display order.

    Only includes: Final, Comment, Addendum, Microscopic (by CommentType.Code).
    Segments are returned in that fixed order regardless of DB ordering.
    """
    rows = (
        db.query(VCaseCommentText, CommentTypeModel.Code)
        .join(CommentTypeModel, VCaseCommentText.CommentTypeId == CommentTypeModel.CommentTypeId)
        .filter(VCaseCommentText.CaseId == case_id)
        .filter(CommentTypeModel.Code.in_(_EXTRACTION_COMMENT_CODES))
        .all()
    )
    rows.sort(key=lambda r: _EXTRACTION_CODE_ORDER.get(r[1], 99))
    return [r[0] for r in rows]


def build_labelled_report_text(segments: List[VCaseCommentText]) -> str:
    """Build a structured, labelled text string from comment segments.

    Example output:
        Final Diagnosis:
        Invasive ductal carcinoma, grade 2...

        Microscopic Description:
        Sections show...
    """
    parts = []
    for seg in segments:
        parts.append(f"{seg.CommentType}:\n{seg.CommentText}")
    return "\n\n".join(parts)


def get_case_text_for_extraction(
    case_id: int,
    db: Session,
    role: Optional[str] = None,
) -> tuple[str, List[VCaseCommentText]]:
    """Return (labelled_text, segments) for LLM input.

    Applies DEMOADMIN masking if role == 'DEMOADMIN'.
    """
    segments = get_case_text_segments(case_id, db)

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
    total = (
        db.query(ExtractionQueue)
        .filter(ExtractionQueue.ExtractionSessionId == session_id)
        .count()
    )

    if latest_run is None:
        return {
            "session_id": session_id,
            "run_id": None,
            "status": session.Status if session else "unknown",
            "total": total,
            "completed": 0,
            "failed": 0,
        }

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
