from datetime import datetime

from core.constants import Constants
from db.models.CytologyEvaluation import CytologyEvaluation
from db.models.CytologyEvaluationSite import CytologyEvaluationSite
from db.repository.cytology_terminology import is_valid_terminology_value
from exception.data_exception import DataException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from viewmodel.cytology_evaluation import (
    CytologyEvaluationSaveVM,
    CytologyEvaluationSiteInputVM,
)

_EVALUATION_LOAD_OPTIONS = (
    joinedload(CytologyEvaluation.AssignedTo),
    joinedload(CytologyEvaluation.CytologyPersonnel),
    joinedload(CytologyEvaluation.Pathologist),
    joinedload(CytologyEvaluation.Fellow),
    joinedload(CytologyEvaluation.Resident),
    joinedload(CytologyEvaluation.PrelimVerifier),
    joinedload(CytologyEvaluation.FinalVerifier),
    joinedload(CytologyEvaluation.Sites),
)


def get_cytology_evaluation(evaluation_id: int, db: Session) -> CytologyEvaluation:
    evaluation = (
        db.query(CytologyEvaluation)
        .options(*_EVALUATION_LOAD_OPTIONS)
        .filter(CytologyEvaluation.CytologyEvaluationId == evaluation_id)
        .first()
    )
    if evaluation is None:
        raise DataException("Cytology evaluation does not exist")
    return evaluation


def user_can_access_evaluation(
    evaluation: CytologyEvaluation, user_id: int, user_nuid: str
) -> bool:
    """Same visibility rule used for the worklist: one of the five assignment
    roles, or the original creator."""
    assigned_user_ids = {
        evaluation.AssignedToUserId,
        evaluation.CytologyPersonnelUserId,
        evaluation.PathologistUserId,
        evaluation.FellowUserId,
        evaluation.ResidentUserId,
    }
    return user_id in assigned_user_ids or evaluation.CreateBy == user_nuid


def list_cytology_evaluations(
    db: Session, user_id: int, user_nuid: str
):
    """Returns only evaluations visible to the given user: anyone named in one
    of the five assignment roles (Assigned/Cytology Personnel/Pathologist/
    Fellow/Resident), plus the original creator (so a user who creates a
    draft without yet naming themselves in one of those roles doesn't
    immediately lose visibility of their own new evaluation)."""
    return (
        db.query(CytologyEvaluation)
        .options(*_EVALUATION_LOAD_OPTIONS)
        .filter(
            or_(
                CytologyEvaluation.AssignedToUserId == user_id,
                CytologyEvaluation.CytologyPersonnelUserId == user_id,
                CytologyEvaluation.PathologistUserId == user_id,
                CytologyEvaluation.FellowUserId == user_id,
                CytologyEvaluation.ResidentUserId == user_id,
                CytologyEvaluation.CreateBy == user_nuid,
            )
        )
        .order_by(CytologyEvaluation.CreateDate.desc())
        .all()
    )


def list_completed_cytology_evaluations(
    db: Session, user_id: int, user_nuid: str
):
    """Same visibility rule as list_cytology_evaluations, restricted to
    evaluations that have completed final verification."""
    return (
        db.query(CytologyEvaluation)
        .options(*_EVALUATION_LOAD_OPTIONS)
        .filter(
            CytologyEvaluation.Status
            == Constants.CytologyEvaluationStatus.FINAL_VERIFIED.value
        )
        .filter(
            or_(
                CytologyEvaluation.AssignedToUserId == user_id,
                CytologyEvaluation.CytologyPersonnelUserId == user_id,
                CytologyEvaluation.PathologistUserId == user_id,
                CytologyEvaluation.FellowUserId == user_id,
                CytologyEvaluation.ResidentUserId == user_id,
                CytologyEvaluation.CreateBy == user_nuid,
            )
        )
        .order_by(CytologyEvaluation.FinalVerifiedDate.desc())
        .all()
    )


def _validate_terminology_fields(input: CytologyEvaluationSaveVM, db: Session):
    checks = (
        (
            Constants.CytologyTerminologyCategory.PROCEDURE_TYPE.value,
            input.procedureType,
            "Procedure type",
        ),
        (
            Constants.CytologyTerminologyCategory.READ_LOCATION.value,
            input.readLocation,
            "Read location",
        ),
        (
            Constants.CytologyTerminologyCategory.PROCEDURE_LOCATION.value,
            input.procedureLocation,
            "Procedure location",
        ),
    )
    for category, value, label in checks:
        if value and not is_valid_terminology_value(db, category, value):
            raise DataException(
                f"{label} '{value}' is not a recognized terminology value"
            )

    for site_input in input.sites:
        if site_input.site and not is_valid_terminology_value(
            db, Constants.CytologyTerminologyCategory.SITE.value, site_input.site
        ):
            raise DataException(
                f"Site '{site_input.site}' is not a recognized terminology value"
            )
        if site_input.adequacy and not is_valid_terminology_value(
            db,
            Constants.CytologyTerminologyCategory.ADEQUACY.value,
            site_input.adequacy,
        ):
            raise DataException(
                f"Adequacy value '{site_input.adequacy}' is not a recognized "
                "terminology value"
            )


def _apply_form_fields(
    evaluation: CytologyEvaluation, input: CytologyEvaluationSaveVM, user: str
):
    evaluation.PatientIdentifiers = input.patientIdentifiers
    evaluation.ProcedureType = input.procedureType
    evaluation.ProcedurePerformedBy = input.procedurePerformedBy
    evaluation.EvaluationPerformedBy = input.evaluationPerformedBy
    evaluation.ViaTelecytology = input.viaTelecytology
    evaluation.ReadLocation = input.readLocation
    evaluation.ProcedureLocation = input.procedureLocation
    evaluation.AssignedToUserId = input.assignedToUserId
    evaluation.ClinicalHistory = input.clinicalHistory
    evaluation.Notes = input.notes
    evaluation.PatientHistory = input.patientHistory
    evaluation.CytologyPersonnelUserId = input.cytologyPersonnelUserId
    evaluation.PathologistUserId = input.pathologistUserId
    evaluation.FellowUserId = input.fellowUserId
    evaluation.ResidentUserId = input.residentUserId
    evaluation.TotalTimeSpentMinutes = input.totalTimeSpentMinutes
    evaluation.UpdateBy = user


def _build_site(site_input: CytologyEvaluationSiteInputVM, sort_order: int, user: str):
    return CytologyEvaluationSite(
        Site=site_input.site,
        EvalEpisodeNumber=site_input.evalEpisodeNumber,
        Adequacy=site_input.adequacy,
        DQCount=site_input.dqCount,
        PapCount=site_input.papCount,
        ThinPrepCount=site_input.thinPrepCount,
        CellBlockCount=site_input.cellBlockCount,
        UnstainedSlidesCount=site_input.unstainedSlidesCount,
        SortOrder=sort_order,
        CreateBy=user,
    )


def _sync_sites(
    evaluation: CytologyEvaluation,
    site_inputs: list[CytologyEvaluationSiteInputVM],
    user: str,
):
    existing_by_id = {
        site.CytologyEvaluationSiteId: site for site in evaluation.Sites
    }
    updated_sites = []
    for sort_order, site_input in enumerate(site_inputs):
        if site_input.id is not None and site_input.id in existing_by_id:
            site = existing_by_id[site_input.id]
            site.Site = site_input.site
            site.EvalEpisodeNumber = site_input.evalEpisodeNumber
            site.Adequacy = site_input.adequacy
            site.DQCount = site_input.dqCount
            site.PapCount = site_input.papCount
            site.ThinPrepCount = site_input.thinPrepCount
            site.CellBlockCount = site_input.cellBlockCount
            site.UnstainedSlidesCount = site_input.unstainedSlidesCount
            site.SortOrder = sort_order
            site.UpdateBy = user
            updated_sites.append(site)
        else:
            updated_sites.append(_build_site(site_input, sort_order, user))
    # Reassigning triggers the "all, delete-orphan" cascade for any removed
    # site entries, and inserts newly-added entries.
    evaluation.Sites = updated_sites


def create_cytology_evaluation(
    input: CytologyEvaluationSaveVM, user: str, db: Session
) -> CytologyEvaluation:
    _validate_terminology_fields(input, db)
    evaluation = CytologyEvaluation(
        Status=Constants.CytologyEvaluationStatus.DRAFT.value,
        CreateBy=user,
    )
    _apply_form_fields(evaluation, input, user)
    db.add(evaluation)
    db.flush()
    _sync_sites(evaluation, input.sites, user)
    db.commit()
    return get_cytology_evaluation(evaluation.CytologyEvaluationId, db=db)


def save_cytology_evaluation(
    evaluation_id: int,
    input: CytologyEvaluationSaveVM,
    user: str,
    db: Session,
) -> CytologyEvaluation:
    evaluation = get_cytology_evaluation(evaluation_id, db=db)
    _validate_terminology_fields(input, db)
    _apply_form_fields(evaluation, input, user)
    _sync_sites(evaluation, input.sites, user)
    db.commit()
    return get_cytology_evaluation(evaluation_id, db=db)


def delete_cytology_evaluation(
    evaluation_id: int, user_id: int, user_nuid: str, db: Session
) -> None:
    evaluation = get_cytology_evaluation(evaluation_id, db=db)
    if not user_can_access_evaluation(evaluation, user_id, user_nuid):
        raise DataException(
            "You do not have access to delete this evaluation"
        )
    if evaluation.Status != Constants.CytologyEvaluationStatus.DRAFT.value:
        raise DataException(
            "Only evaluations still in Draft status can be deleted"
        )
    db.delete(evaluation)
    db.commit()


def _require_valid_sites_for_verification(
    evaluation: CytologyEvaluation, require_adequacy: bool
):
    if not evaluation.Sites:
        raise DataException(
            "At least one specimen-site entry is required before verification"
        )
    for site in evaluation.Sites:
        if not site.Site:
            raise DataException(
                "Every specimen-site entry must have a Site selected before "
                "verification"
            )
        if require_adequacy and not site.Adequacy:
            raise DataException(
                "Every specimen-site entry must have an Adequacy/Preliminary "
                "Interpretation/Intraoperative Consultation value before "
                "final verification"
            )


def prelim_verify_cytology_evaluation(
    evaluation_id: int, user_id: int, user: str, db: Session
) -> CytologyEvaluation:
    evaluation = get_cytology_evaluation(evaluation_id, db=db)
    if not evaluation.ProcedureType:
        raise DataException("Procedure type is required before preliminary verification")
    _require_valid_sites_for_verification(evaluation, require_adequacy=False)

    evaluation.PrelimVerifierId = user_id
    evaluation.PrelimVerifiedDate = datetime.now().replace(tzinfo=None)
    evaluation.Status = Constants.CytologyEvaluationStatus.PRELIM_VERIFIED.value
    evaluation.UpdateBy = user
    db.commit()
    return get_cytology_evaluation(evaluation_id, db=db)


def final_verify_cytology_evaluation(
    evaluation_id: int, user_id: int, user: str, db: Session
) -> CytologyEvaluation:
    evaluation = get_cytology_evaluation(evaluation_id, db=db)
    _require_valid_sites_for_verification(evaluation, require_adequacy=True)

    evaluation.FinalVerifierId = user_id
    evaluation.FinalVerifiedDate = datetime.now().replace(tzinfo=None)
    evaluation.Status = Constants.CytologyEvaluationStatus.FINAL_VERIFIED.value
    evaluation.UpdateBy = user
    db.commit()
    return get_cytology_evaluation(evaluation_id, db=db)
