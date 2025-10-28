from typing import Annotated
from typing import List
from db.repository.auditTrailCaseInfo import create_audit_case

from core.auth_bearer import JWTBearer
from core.security_user import (
    get_current_user_nuid,
    get_current_user_role,
    get_current_user_id,
    get_current_user_attest,
)
from db.repository.case import get_case
from db.repository.annotationConfiguration import list_config
from db.session import get_db
from fastapi import APIRouter, Depends
from pytest import Session
from viewmodel.views.case import CaseInputVM, ResultVM
from viewmodel.annotationConfiguration import AnnotationConfigurationVM
from core.security_util import SecurityUtil
from logger import logger

router = APIRouter()


@router.post(
    "/caseinfo", dependencies=[Depends(JWTBearer())], response_model=ResultVM
)
async def case_info(
    input: CaseInputVM,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_role: Annotated[str, Depends(get_current_user_role)],
    current_is_attest: Annotated[str, Depends(get_current_user_attest)],
    db: Session = Depends(get_db),
):
    case = get_case(caseId=input.caseid, db=db)
    try:
        create_audit_case(
            userId=current_user_id,
            user=current_user,
            caseId=input.caseid,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Case audit error - create_audit_case 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )

    attrExcludes = SecurityUtil.case(
        case["case"], current_role, current_is_attest
    )
    case["attrExcludes"] = attrExcludes
    return case


@router.get(
    "/annotationconfig",
    dependencies=[Depends(JWTBearer())],
    response_model=List[AnnotationConfigurationVM],
)
async def case_annotation_config(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    config = list_config(db=db)
    return config
