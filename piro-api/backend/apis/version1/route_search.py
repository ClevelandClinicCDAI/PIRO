from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.search import (
    create_new_search,
    delete_search,
    get_search,
    get_search_display,
    list_search,
    list_search_active,
    update_search,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.search import (
    SearchVM,
    SearchVMCreate,
    SearchVMDropdown,
    SearchVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleUser,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
    response_model=SearchVM,
)
async def create_search(
    search: SearchVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = create_new_search(
        input=search, user=current_user, userId=current_user_id, db=db
    )
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleUser,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
    response_model=SearchVM,
)
async def update__search(
    search: SearchVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_search(input=search, user=current_user, db=db)
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[SearchVM]
)
async def read_search_all(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    searchs = list_search(db=db, userId=current_user_id)
    return paginate(searchs)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchVM],
)
async def read_search_all_active(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    searchs = list_search_active(db=db, userId=current_user_id)
    return paginate(searchs)


@router.get(
    "/dropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SearchVMDropdown],
)
async def read_search_all_dropdown(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    searchs = list_search_active(db=db, userId=current_user_id)
    return searchs


@router.get(
    "/get/{searchId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SearchVM,
)
async def get(searchId: int, db: Session = Depends(get_db)):
    search = get_search(searchId=searchId, db=db)
    return search


@router.get(
    "/display/{searchId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SearchVM,
)
async def display(searchId: int, db: Session = Depends(get_db)):
    search = get_search_display(searchId=searchId, db=db)
    return search


@router.delete(
    "/delete/{searchId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleUser,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
    response_model=SearchVM,
)
async def delete(searchId: int, db: Session = Depends(get_db)):
    search = delete_search(searchId=searchId, db=db)
    return search
