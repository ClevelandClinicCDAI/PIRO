from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.cytology_evaluation import (
    create_cytology_evaluation,
    delete_cytology_evaluation,
    final_verify_cytology_evaluation,
    get_cytology_evaluation,
    list_completed_cytology_evaluations,
    list_cytology_evaluations,
    prelim_verify_cytology_evaluation,
    save_cytology_evaluation,
    user_can_access_evaluation,
)
from db.repository.cytology_terminology import get_cytology_terminology
from db.session import get_db
from exception.data_exception import DataException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.cytology_evaluation import (
    CytologyEvaluationSaveVM,
    CytologyEvaluationVM,
    CytologyTerminologyVM,
    to_cytology_evaluation_vm,
)

router = APIRouter()


def _require_access(evaluation, user_id: int, user_nuid: str):
    """Raises if the acting user isn't one of the five assignment roles (or
    the original creator) on this evaluation. Evaluations are private to
    those users only."""
    if not user_can_access_evaluation(evaluation, user_id, user_nuid):
        raise DataException("You do not have access to this evaluation")


@router.get(
    "/terminology",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyTerminologyVM,
)
async def read_terminology(db: Session = Depends(get_db)):
    return get_cytology_terminology(db=db)


@router.post(
    "",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyEvaluationVM,
)
async def create_evaluation(
    payload: CytologyEvaluationSaveVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    evaluation = create_cytology_evaluation(
        input=payload, user=current_user, db=db
    )
    return to_cytology_evaluation_vm(evaluation)


@router.get(
    "",
    dependencies=[Depends(JWTBearer())],
    response_model=List[CytologyEvaluationVM],
)
async def list_evaluations(
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """Only returns evaluations where the current user is named as one of the
    five assignment roles, or is the original creator."""
    evaluations = list_cytology_evaluations(
        db=db, user_id=int(current_user_id), user_nuid=current_user
    )
    return [to_cytology_evaluation_vm(item) for item in evaluations]


@router.get(
    "/completed",
    dependencies=[Depends(JWTBearer())],
    response_model=List[CytologyEvaluationVM],
)
async def list_completed_evaluations(
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """Same visibility rule as the main worklist, restricted to Final
    Verified evaluations, for the read-only 'completed evaluations' view."""
    evaluations = list_completed_cytology_evaluations(
        db=db, user_id=int(current_user_id), user_nuid=current_user
    )
    return [to_cytology_evaluation_vm(item) for item in evaluations]


@router.get(
    "/{evaluation_id}",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyEvaluationVM,
)
async def get_evaluation(
    evaluation_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    evaluation = get_cytology_evaluation(evaluation_id, db=db)
    _require_access(evaluation, int(current_user_id), current_user)
    return to_cytology_evaluation_vm(evaluation)


@router.put(
    "/{evaluation_id}",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyEvaluationVM,
)
async def save_evaluation(
    evaluation_id: int,
    payload: CytologyEvaluationSaveVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """Saves form-level changes and syncs specimen-site entries (add / update /
    remove). Used for both draft saves and edits after preliminary
    verification."""
    existing = get_cytology_evaluation(evaluation_id, db=db)
    _require_access(existing, int(current_user_id), current_user)
    evaluation = save_cytology_evaluation(
        evaluation_id=evaluation_id, input=payload, user=current_user, db=db
    )
    return to_cytology_evaluation_vm(evaluation)


@router.delete(
    "/{evaluation_id}",
    dependencies=[Depends(JWTBearer())],
)
async def delete_evaluation(
    evaluation_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """Only allowed for Draft evaluations, and only by a user with access to
    the evaluation (one of the five assignment roles, or its creator)."""
    delete_cytology_evaluation(
        evaluation_id=evaluation_id,
        user_id=int(current_user_id),
        user_nuid=current_user,
        db=db,
    )
    return {"deleted": True}


@router.post(
    "/{evaluation_id}/prelim-verify",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyEvaluationVM,
)
async def prelim_verify(
    evaluation_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """The acting user's NUID/UserId is always derived from the authenticated
    session; the client cannot supply a verifier identity."""
    existing = get_cytology_evaluation(evaluation_id, db=db)
    _require_access(existing, int(current_user_id), current_user)
    evaluation = prelim_verify_cytology_evaluation(
        evaluation_id=evaluation_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_cytology_evaluation_vm(evaluation)


@router.post(
    "/{evaluation_id}/final-verify",
    dependencies=[Depends(JWTBearer())],
    response_model=CytologyEvaluationVM,
)
async def final_verify(
    evaluation_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    existing = get_cytology_evaluation(evaluation_id, db=db)
    _require_access(existing, int(current_user_id), current_user)
    evaluation = final_verify_cytology_evaluation(
        evaluation_id=evaluation_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_cytology_evaluation_vm(evaluation)
