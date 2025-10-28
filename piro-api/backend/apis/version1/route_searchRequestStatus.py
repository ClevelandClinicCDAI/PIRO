from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.searchRequestStatus import (
    create_new_searchRequestStatus,
    delete_searchRequestStatus,
    get_searchRequestStatus,
    list_searchRequestStatus,
    list_searchRequestStatus_active,
    update_searchRequestStatus,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.searchRequestStatus import (
    SearchRequestStatusVM,
    SearchRequestStatusVMCreate,
    SearchRequestStatusVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SearchRequestStatusVM,
)
async def create_searchRequestStatus(
    searchRequestStatus: SearchRequestStatusVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_searchRequestStatus(
        input=searchRequestStatus, user=current_user, db=db
    )
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SearchRequestStatusVM,
)
async def update__searchRequestStatus(
    searchRequestStatus: SearchRequestStatusVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_searchRequestStatus(
        input=searchRequestStatus, user=current_user, db=db
    )
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestStatusVM],
)
async def read_searchRequestStatus_all(db: Session = Depends(get_db)):
    searchRequestStatuss = list_searchRequestStatus(db=db)
    return paginate(searchRequestStatuss)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestStatusVM],
)
async def read_searchRequestStatus_all_active(db: Session = Depends(get_db)):
    searchRequestStatuss = list_searchRequestStatus_active(db=db)
    return paginate(searchRequestStatuss)


@router.get(
    "/get/{searchRequestStatusId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SearchRequestStatusVM,
)
async def get(searchRequestStatusId: int, db: Session = Depends(get_db)):
    searchRequestStatus = get_searchRequestStatus(
        searchRequestStatusId=searchRequestStatusId, db=db
    )
    return searchRequestStatus


@router.delete(
    "/delete/{searchRequestStatusId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SearchRequestStatusVM,
)
async def delete(searchRequestStatusId: int, db: Session = Depends(get_db)):
    searchRequestStatus = delete_searchRequestStatus(
        searchRequestStatusId=searchRequestStatusId, db=db
    )
    return searchRequestStatus
