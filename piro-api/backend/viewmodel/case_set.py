from typing import ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, Field, conint, conlist, constr, root_validator
from striprtf.striprtf import rtf_to_text

from viewmodel.solr.search import SearchDocumentVM


class CaseSetDocumentVM(SearchDocumentVM):
    """Full report text for individual case review; search previews stay bounded."""

    report_text_limit: ClassVar[int | None] = None
    grosstexts: list[str] = Field(default_factory=list, exclude=False)

    @root_validator
    def omit_blank_sections(cls, values):
        for field in (
            "finaltexts",
            "commenttexts",
            "grosstexts",
            "synoptictexts",
            "intraoptexts",
            "microscopictexts",
        ):
            texts = []
            for value in values.get(field) or []:
                readable = value
                if value.startswith("{\\rtf1"):
                    try:
                        readable = rtf_to_text(value)
                    except Exception:
                        pass  # Keep malformed source text available for the renderer.
                if readable.strip():
                    texts.append(value)
            values[field] = texts
        return values


ReviewState = Literal["UNREVIEWED", "INCLUDED", "EXCLUDED"]
ReviewFilter = Literal["ALL", "UNREVIEWED", "INCLUDED", "EXCLUDED"]
SetOperation = Literal["UNION", "INTERSECTION", "DIFFERENCE", "SYMMETRIC_DIFFERENCE"]
MembershipPolicy = Literal["NOT_EXCLUDED", "INCLUDED_ONLY"]


class CaseSetOperationPreview(BaseModel):
    leftSetId: int = Field(gt=0)
    rightSetId: int = Field(gt=0)
    operation: SetOperation
    membership: MembershipPolicy = "NOT_EXCLUDED"


class CaseSetOperationCreate(CaseSetOperationPreview):
    name: constr(strip_whitespace=True, min_length=1, max_length=250)
    description: constr(max_length=2000) = ""
    leftRevision: int = Field(ge=0)
    rightRevision: int = Field(ge=0)
    operationId: UUID


class CaseSetCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=250)
    description: constr(max_length=2000) = ""
    sourceType: Literal["SAVED_SEARCH", "COHORT"]
    sourceId: int = Field(gt=0)
    operationId: UUID


class CaseSetAddCases(BaseModel):
    caseIds: conlist(conint(strict=True, gt=0), min_items=1, max_items=1000)


class CaseSetCartCreate(CaseSetAddCases):
    name: constr(strip_whitespace=True, min_length=1, max_length=250)
    description: constr(max_length=2000) = ""
    operationId: UUID


class CaseSetEdit(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=250)
    description: constr(max_length=2000) = ""
    archived: bool
    revision: int = Field(ge=0)


class CaseSetSharing(BaseModel):
    isPublic: bool
    specialtyCategory: constr(strip_whitespace=True, max_length=100) | None = None
    revision: int = Field(ge=0)


class CaseSetCapture(BaseModel):
    cursor: str = Field(min_length=1)


class CaseSetDecision(BaseModel):
    state: ReviewState
    revision: int = Field(ge=0)


class CaseSetSpecimenSelection(BaseModel):
    specimenIds: conlist(conint(strict=True, gt=0), max_items=2000)
    revision: int = Field(ge=0)


class CaseSetPosition(BaseModel):
    caseId: int | None = Field(default=None, gt=0)
    filter: ReviewFilter = "ALL"
