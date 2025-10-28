from typing import Annotated, List
from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid, get_current_user_id
from db.repository.annotationCaseFeedback import (
    create_new_feedback,
    update_review,
    search_feedback,
    pending_review,
    feedback_data,
)
from db.repository.auditCaseAnnotation import list_case_annotation
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.annotationCaseFeedback import (
    AnnotationCaseFeedbackVM,
    AnnotationCaseFeedbackVMCreate,
    AnnotationCaseFeedbackVMSearch,
    AnnotationCaseFeedbackDataVM,
)
from viewmodel.auditCaseAnnotation import (
    AuditCaseAnnotationVM,
    AuditCaseAnnotationVMSearch,
)

router = APIRouter()


@router.post(
    "/createfeedback",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
    response_model=bool,
)
async def create_feedback(
    input: AnnotationCaseFeedbackVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    create_new_feedback(
        input=input, userId=current_userid, user=current_user, db=db
    )
    return True


@router.post(
    "/updatefeedback",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=bool,
)
async def update_feedback(
    input: AnnotationCaseFeedbackVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    update_review(input=input, user=current_user, db=db)
    return True


@router.post(
    "/getfeedback",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=List[AnnotationCaseFeedbackVM],
)
async def get_feedback(
    input: AnnotationCaseFeedbackVMSearch,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    # result = search_feedback(input=input, db=db)
    result = search_feedback(
        caseid=input.caseid,
        casenum=input.casenum,
        annotationConfigurationId=input.annotationConfigurationId,
        feedback=input.feedback,
        pending=input.pending,
        db=db,
    )
    return result


@router.get(
    "/getfeedbackall",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=Page[AnnotationCaseFeedbackVM],
)
async def get_feedback_all(
    caseid: int,
    casenum: str,
    annotationConfigurationId: int,
    feedback: int,
    pending: bool,
    size: int,
    page: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = search_feedback(
        caseid=caseid,
        casenum=casenum,
        annotationConfigurationId=annotationConfigurationId,
        feedback=feedback,
        pending=pending,
        db=db,
    )
    # result = []
    return paginate(result)


@router.get(
    "/ispendingreview",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=bool,
)
async def get_pending_review(
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = pending_review(db=db)
    return result


@router.post(
    "/getaudit",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=List[AuditCaseAnnotationVM],
)
async def get_audit(
    input: AuditCaseAnnotationVMSearch,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = list_case_annotation(
        caseId=input.caseid, configId=input.configid, db=db
    )
    return result


@router.post(
    "/getfeedbackdata",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
    response_model=AnnotationCaseFeedbackDataVM,
)
async def get_feedback_data(
    input: AuditCaseAnnotationVMSearch,
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = feedback_data(
        caseId=input.caseid,
        configId=input.configid,
        userId=current_userid,
        db=db,
    )
    return result
