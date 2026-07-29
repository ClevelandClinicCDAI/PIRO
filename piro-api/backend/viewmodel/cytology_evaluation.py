from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from core.constants import Constants
from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:  # pragma: no cover
    from db.models.CytologyEvaluation import CytologyEvaluation
    from db.models.CytologyEvaluationSite import CytologyEvaluationSite


def _format_user_name(user) -> Optional[str]:
    if user is None:
        return None
    first = getattr(user, "FirstName", "") or ""
    last = getattr(user, "LastName", "") or ""
    if first and last:
        return f"{last}, {first}"
    return first or last


class CytologyEvaluationSiteInputVM(BaseModel):
    id: Optional[int] = Field(default=None)
    site: Optional[str] = Field(default=None, max_length=200)
    evalEpisodeNumber: Optional[int] = Field(default=None)
    adequacy: Optional[str] = Field(default=None, max_length=500)
    dqCount: int = Field(default=0)
    papCount: int = Field(default=0)
    thinPrepCount: int = Field(default=0)
    cellBlockCount: int = Field(default=0)
    unstainedSlidesCount: int = Field(default=0)

    @validator(
        "dqCount",
        "papCount",
        "thinPrepCount",
        "cellBlockCount",
        "unstainedSlidesCount",
    )
    def _validate_non_negative_whole_number(
        cls, value: int
    ):  # pylint: disable=no-self-argument
        if value is None:
            return 0
        if value < 0:
            raise ValueError("Slide/block counts must not be negative")
        return value

    @validator("evalEpisodeNumber")
    def _validate_eval_episode_number(
        cls, value: Optional[int]
    ):  # pylint: disable=no-self-argument
        if value is not None and value < 0:
            raise ValueError("Evaluation episode number must not be negative")
        return value


class CytologyEvaluationSiteVM(BaseModel):
    id: int
    site: Optional[str] = None
    evalEpisodeNumber: Optional[int] = None
    adequacy: Optional[str] = None
    dqCount: int
    papCount: int
    thinPrepCount: int
    cellBlockCount: int
    unstainedSlidesCount: int
    sortOrder: int


class CytologyEvaluationTotalsVM(BaseModel):
    totalDQ: int
    totalPap: int
    totalThinPrep: int
    totalCellBlock: int
    totalUnstainedSlides: int


class CytologyEvaluationSaveVM(BaseModel):
    """Payload used to create a draft or save form-level + site changes."""

    patientIdentifiers: Optional[str] = Field(default=None, max_length=500)
    procedureType: Optional[str] = Field(default=None, max_length=100)
    procedurePerformedBy: Optional[str] = Field(default=None, max_length=100)
    evaluationPerformedBy: Optional[str] = Field(default=None, max_length=100)
    viaTelecytology: Optional[bool] = Field(default=None)
    readLocation: Optional[str] = Field(default=None, max_length=200)
    procedureLocation: Optional[str] = Field(default=None, max_length=200)
    assignedToUserId: Optional[int] = Field(default=None)
    clinicalHistory: Optional[str] = Field(default=None, max_length=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    patientHistory: Optional[str] = Field(default=None)
    cytologyPersonnelUserId: Optional[int] = Field(default=None)
    pathologistUserId: Optional[int] = Field(default=None)
    fellowUserId: Optional[int] = Field(default=None)
    residentUserId: Optional[int] = Field(default=None)
    totalTimeSpentMinutes: Optional[int] = Field(default=None)
    sites: List[CytologyEvaluationSiteInputVM] = Field(default_factory=list)

    @validator("totalTimeSpentMinutes")
    def _validate_total_time_spent(
        cls, value: Optional[int]
    ):  # pylint: disable=no-self-argument
        if value is not None and value < 0:
            raise ValueError("Total time spent must not be negative")
        return value


class CytologyEvaluationVM(BaseModel):
    id: int
    status: Constants.CytologyEvaluationStatus
    patientIdentifiers: Optional[str] = None
    procedureType: Optional[str] = None
    procedurePerformedBy: Optional[str] = None
    evaluationPerformedBy: Optional[str] = None
    viaTelecytology: Optional[bool] = None
    readLocation: Optional[str] = None
    procedureLocation: Optional[str] = None
    assignedToUserId: Optional[int] = None
    assignedToName: Optional[str] = None
    clinicalHistory: Optional[str] = None
    notes: Optional[str] = None
    patientHistory: Optional[str] = None
    cytologyPersonnelUserId: Optional[int] = None
    cytologyPersonnelName: Optional[str] = None
    pathologistUserId: Optional[int] = None
    pathologistName: Optional[str] = None
    fellowUserId: Optional[int] = None
    fellowName: Optional[str] = None
    residentUserId: Optional[int] = None
    residentName: Optional[str] = None
    totalTimeSpentMinutes: Optional[int] = None
    prelimVerifierNuid: Optional[str] = None
    prelimVerifierName: Optional[str] = None
    prelimVerifiedDate: Optional[datetime] = None
    finalVerifierNuid: Optional[str] = None
    finalVerifierName: Optional[str] = None
    finalVerifiedDate: Optional[datetime] = None
    createDate: datetime
    updateDate: Optional[datetime] = None
    sites: List[CytologyEvaluationSiteVM]
    totals: CytologyEvaluationTotalsVM


class CytologyTerminologyVM(BaseModel):
    procedureType: List[str]
    readLocation: List[str]
    procedureLocation: List[str]
    site: List[str]
    adequacy: List[str]


def calculate_totals(
    sites: List["CytologyEvaluationSite"],
) -> CytologyEvaluationTotalsVM:
    return CytologyEvaluationTotalsVM(
        totalDQ=sum(site.DQCount or 0 for site in sites),
        totalPap=sum(site.PapCount or 0 for site in sites),
        totalThinPrep=sum(site.ThinPrepCount or 0 for site in sites),
        totalCellBlock=sum(site.CellBlockCount or 0 for site in sites),
        totalUnstainedSlides=sum(
            site.UnstainedSlidesCount or 0 for site in sites
        ),
    )


def to_site_vm(site: "CytologyEvaluationSite") -> CytologyEvaluationSiteVM:
    return CytologyEvaluationSiteVM(
        id=site.CytologyEvaluationSiteId,
        site=site.Site,
        evalEpisodeNumber=site.EvalEpisodeNumber,
        adequacy=site.Adequacy,
        dqCount=site.DQCount,
        papCount=site.PapCount,
        thinPrepCount=site.ThinPrepCount,
        cellBlockCount=site.CellBlockCount,
        unstainedSlidesCount=site.UnstainedSlidesCount,
        sortOrder=site.SortOrder,
    )


def to_cytology_evaluation_vm(
    evaluation: "CytologyEvaluation",
) -> CytologyEvaluationVM:
    return CytologyEvaluationVM(
        id=evaluation.CytologyEvaluationId,
        status=evaluation.Status,
        patientIdentifiers=evaluation.PatientIdentifiers,
        procedureType=evaluation.ProcedureType,
        procedurePerformedBy=evaluation.ProcedurePerformedBy,
        evaluationPerformedBy=evaluation.EvaluationPerformedBy,
        viaTelecytology=evaluation.ViaTelecytology,
        readLocation=evaluation.ReadLocation,
        procedureLocation=evaluation.ProcedureLocation,
        assignedToUserId=evaluation.AssignedToUserId,
        assignedToName=_format_user_name(evaluation.AssignedTo),
        clinicalHistory=evaluation.ClinicalHistory,
        notes=evaluation.Notes,
        patientHistory=evaluation.PatientHistory,
        cytologyPersonnelUserId=evaluation.CytologyPersonnelUserId,
        cytologyPersonnelName=_format_user_name(evaluation.CytologyPersonnel),
        pathologistUserId=evaluation.PathologistUserId,
        pathologistName=_format_user_name(evaluation.Pathologist),
        fellowUserId=evaluation.FellowUserId,
        fellowName=_format_user_name(evaluation.Fellow),
        residentUserId=evaluation.ResidentUserId,
        residentName=_format_user_name(evaluation.Resident),
        totalTimeSpentMinutes=evaluation.TotalTimeSpentMinutes,
        prelimVerifierNuid=(
            evaluation.PrelimVerifier.NUID
            if evaluation.PrelimVerifier
            else None
        ),
        prelimVerifierName=_format_user_name(evaluation.PrelimVerifier),
        prelimVerifiedDate=evaluation.PrelimVerifiedDate,
        finalVerifierNuid=(
            evaluation.FinalVerifier.NUID if evaluation.FinalVerifier else None
        ),
        finalVerifierName=_format_user_name(evaluation.FinalVerifier),
        finalVerifiedDate=evaluation.FinalVerifiedDate,
        createDate=evaluation.CreateDate,
        updateDate=evaluation.UpdateDate,
        sites=[to_site_vm(site) for site in evaluation.Sites],
        totals=calculate_totals(evaluation.Sites),
    )
