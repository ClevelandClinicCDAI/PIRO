from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ──────────────────────────────────────────────────────────────────────────────
# Session
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionSessionCreate(BaseModel):
    name: str
    schema_definition: Optional[str] = None


class ExtractionSessionUpdate(BaseModel):
    name: Optional[str] = None
    schema_definition: Optional[str] = None


class ExtractionSessionVM(BaseModel):
    ExtractionSessionId: int
    UserId: int
    Name: str
    SchemaJson: Optional[str] = None
    Status: str
    IsActive: bool
    CreateDate: Optional[datetime] = None

    class Config:
        orm_mode = True


# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionRunVM(BaseModel):
    ExtractionRunId: int
    ExtractionSessionId: int
    LlmProvider: str
    LlmModel: str
    Status: str
    StartedAt: Optional[datetime] = None
    CompletedAt: Optional[datetime] = None
    ErrorMessage: Optional[str] = None
    CreateDate: Optional[datetime] = None

    class Config:
        orm_mode = True


# ──────────────────────────────────────────────────────────────────────────────
# Queue
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionQueueAdd(BaseModel):
    session_id: int
    case_ids: List[int]


class ExtractionQueueFromSearch(BaseModel):
    session_id: int
    search_id: int


class ExtractionQueueItemVM(BaseModel):
    ExtractionQueueId: int
    ExtractionSessionId: int
    CaseId: int
    CaseNumber: Optional[str] = None
    Status: str
    ErrorMessage: Optional[str] = None
    AttemptCount: int
    CreateDate: Optional[datetime] = None

    class Config:
        orm_mode = True


# ──────────────────────────────────────────────────────────────────────────────
# Run request
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionRunRequest(BaseModel):
    session_id: int


class ExtractionStatusVM(BaseModel):
    session_id: int
    run_id: Optional[int] = None
    status: str
    total: int
    completed: int
    failed: int


# ──────────────────────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionResultVM(BaseModel):
    ExtractionResultId: int
    ExtractionRunId: int
    ExtractionSessionId: int
    CaseId: int
    CaseNumber: Optional[str] = None
    FieldName: str
    ExtractedValue: Optional[str] = None
    ReviewedValue: Optional[str] = None
    Confidence: Optional[float] = None
    ProvenanceText: Optional[str] = None
    SourceCommentId: Optional[int] = None
    IsReviewed: bool
    ReviewedBy: Optional[str] = None
    ReviewedDate: Optional[datetime] = None

    class Config:
        orm_mode = True


class ExtractionResultPatch(BaseModel):
    reviewed_value: Optional[str] = None
    is_reviewed: Optional[bool] = None


# ──────────────────────────────────────────────────────────────────────────────
# Field suggestion
# ──────────────────────────────────────────────────────────────────────────────

class FieldSuggestionRequest(BaseModel):
    session_id: Optional[int] = None
    sample_text: Optional[str] = None


class FieldSuggestionVM(BaseModel):
    name: str
    type: str
    hint: Optional[str] = None
    enum_values: Optional[List[str]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None


# ──────────────────────────────────────────────────────────────────────────────
# Preview (single-doc extraction for schema builder)
# ──────────────────────────────────────────────────────────────────────────────

class ExtractionPreviewRequest(BaseModel):
    session_id: int
    case_id: int
    extraction_schema: Dict[str, Any]


class ExtractionPreviewFieldVM(BaseModel):
    value: Any = None
    confidence: Optional[float] = None
    provenance: Optional[str] = None


class ExtractionPreviewVM(BaseModel):
    case_id: int
    extracted_fields: Dict[str, ExtractionPreviewFieldVM]
    report_text: str


# ──────────────────────────────────────────────────────────────────────────────
# Case text
# ──────────────────────────────────────────────────────────────────────────────

class CaseCommentSegmentVM(BaseModel):
    CaseCommentId: int
    CommentType: str
    CommentText: str

    class Config:
        orm_mode = True


class CaseTextVM(BaseModel):
    case_id: int
    segments: List[CaseCommentSegmentVM]
    full_text: str
