from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.auditTrailSearch import (
    list_audit_search,
    list_audit_search_unique,
)
from db.repository.user import update_userprofile
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from pytest import Session
from viewmodel.auditSearch import AuditSearchVM
from viewmodel.user import UserVM, UserVMUpdateProfile

router = APIRouter()


@router.get(
    "/historylatest",
    dependencies=[Depends(JWTBearer())],
    response_model=List[AuditSearchVM],
)
async def search_latest_history(
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    auditTrailSearch = list_audit_search_unique(userId=current_userid, db=db)
    return auditTrailSearch


@router.get(
    "/historyall",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[AuditSearchVM],
)
async def search_all_history(
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    auditTrailSearch = list_audit_search(userId=current_userid, db=db)
    return paginate(auditTrailSearch)


@router.post(
    "/updateprofile",
    dependencies=[Depends(JWTBearer())],
    response_model=UserVM,
)
async def update__user(
    user: UserVMUpdateProfile,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = update_userprofile(
        input=user, userId=current_userid, user=current_user, db=db
    )
    return result
