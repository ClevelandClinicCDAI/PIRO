from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.role import (
    create_new_role,
    delete_role,
    get_role,
    list_role,
    list_role_active,
    update_role,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.role import RoleVM, RoleVMCreate, RoleVMDropdown, RoleVMUpdate

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RoleVM,
)
async def create_role(
    role: RoleVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_role(input=role, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RoleVM,
)
async def update__role(
    role: RoleVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_role(input=role, user=current_user, db=db)
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[RoleVM]
)
async def read_role_all(db: Session = Depends(get_db)):
    roles = list_role(db=db)
    return paginate(roles)


@router.get(
    "/active", dependencies=[Depends(JWTBearer())], response_model=Page[RoleVM]
)
async def read_role_all_active(db: Session = Depends(get_db)):
    roles = list_role_active(db=db)
    return paginate(roles)


@router.get(
    "/dropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[RoleVMDropdown],
)
async def read_role_all_dropdown(db: Session = Depends(get_db)):
    roles = list_role_active(db=db)
    return roles


@router.get(
    "/get/{roleId}", dependencies=[Depends(JWTBearer())], response_model=RoleVM
)
async def get(roleId: int, db: Session = Depends(get_db)):
    role = get_role(roleId=roleId, db=db)
    return role


@router.delete(
    "/delete/{roleId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RoleVM,
)
async def delete(roleId: int, db: Session = Depends(get_db)):
    role = delete_role(roleId=roleId, db=db)
    return role
