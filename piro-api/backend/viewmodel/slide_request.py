from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from core.constants import Constants
from pydantic import BaseModel, Field, root_validator, validator

if TYPE_CHECKING:  # pragma: no cover
    from db.models.SlideRequest import SlideRequest


ACCESSION_PATTERN = re.compile(r"^[A-Za-z]{1,3}\d{2}-\d{3,6}$")


def derive_slide_request_case_type(
    accession_number: str,
) -> Constants.SlideRequestCaseType:
    cleaned = (accession_number or "").strip()
    prefix = cleaned[:1].upper()
    if prefix == "S":
        return Constants.SlideRequestCaseType.SURGICAL
    if prefix == "C":
        return Constants.SlideRequestCaseType.CYTOLOGY
    raise ValueError(
        "Accession number must begin with S for Surgical or C for Cytology"
    )


class SlideRequestCreateVM(BaseModel):
    accessionNumber: str = Field(..., min_length=1, max_length=500)
    urgencyStatus: Constants.SlideRequestUrgency
    reason: Constants.SlideRequestReason
    ePath: bool = Field(default=False)
    requesterNotes: Optional[str] = Field(default=None, max_length=2000)

    @root_validator(pre=True)
    def _coerce_legacy_notes(cls, values):  # pylint: disable=no-self-argument
        if not values.get("requesterNotes") and values.get("notes"):
            values["requesterNotes"] = values["notes"]
        return values

    @validator("accessionNumber")
    def _validate_accession(
        cls, value: str
    ):  # pylint: disable=no-self-argument
        if value is None:
            raise ValueError("Accession number is required")
        cleaned = value.strip()
        if cleaned == "":
            raise ValueError("Accession number is required")
        if not ACCESSION_PATTERN.match(cleaned):
            raise ValueError(
                "Accession number must match format AAA12-123 (1-3 letters, 2 digits, dash, 3-6 digits)"
            )
        derive_slide_request_case_type(cleaned)
        return cleaned

    @validator("requesterNotes")
    def _normalize_requester_notes(
        cls, value: Optional[str]
    ):  # pylint: disable=no-self-argument
        return value.strip() if value else value

    @validator("urgencyStatus")
    def _validate_urgency(
        cls, value: Constants.SlideRequestUrgency
    ):  # pylint: disable=no-self-argument
        if value is None:
            raise ValueError("Urgency status is required")
        return value


class SlideRequestVM(BaseModel):
    id: int
    accessionNumber: str
    caseType: Constants.SlideRequestCaseType
    ePath: bool
    requesterNotes: Optional[str]
    reason: Optional[str]
    status: str
    urgencyStatus: Constants.SlideRequestUrgency
    requestedAt: datetime
    completedAt: Optional[datetime] = None
    requestedBy: Optional[str] = None
    requestedByNuid: Optional[str] = None
    completedBy: Optional[str] = None
    takenBy: Optional[str] = None
    takenByNuid: Optional[str] = None
    slideRoomNotes: Optional[str] = None


class SlideRoomNotesUpdateVM(BaseModel):
    slideRoomNotes: Optional[str] = Field(default=None, max_length=2000)

    @validator("slideRoomNotes")
    def _normalize_notes(
        cls, value: Optional[str]
    ):  # pylint: disable=no-self-argument
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None


def _format_user_name(user) -> Optional[str]:
    if user is None:
        return None
    first = getattr(user, "FirstName", "") or ""
    last = getattr(user, "LastName", "") or ""
    if first and last:
        return f"{last}, {first}"
    return first or last


def to_slide_request_vm(request: "SlideRequest") -> SlideRequestVM:
    return SlideRequestVM(
        id=request.SlideRequestId,
        accessionNumber=request.AccessionNumber,
        caseType=request.CaseType,
        ePath=bool(request.EPath),
        requesterNotes=request.Notes,
        reason=request.Reason,
        status=request.Status,
        urgencyStatus=request.UrgencyStatus,
        requestedAt=request.CreateDate,
        completedAt=request.CompletedDate,
        requestedBy=_format_user_name(request.Requester),
        requestedByNuid=request.Requester.NUID if request.Requester else None,
        completedBy=_format_user_name(request.CompletedBy),
        takenBy=_format_user_name(request.InProcessBy),
        takenByNuid=request.InProcessBy.NUID if request.InProcessBy else None,
        slideRoomNotes=request.SlideRoomNotes,
    )
