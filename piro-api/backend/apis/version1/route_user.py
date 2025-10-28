from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid, get_current_user_role
from db.repository.role import get_role
from db.repository.user import (
    create_new_user,
    delete_user,
    get_user_by_id,
    list_user,
    list_user_active,
    update_user,
)
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.user import UserVM, UserVMCreate, UserVMUpdate

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=UserVM,
)
async def create(
    user: UserVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
    db: Annotated[Session, Depends(get_db)],
):
    role = get_role(user.roleId, db=db)
    if (
        role.Code == Constants.RoleAdmin
        or role.Code == Constants.RoleDemoAdmin
    ):
        if (
            current_user_role == Constants.RoleAdmin
            or current_user_role == Constants.RoleDemoAdmin
        ):
            user = create_new_user(
                input_obj=user, user_name=current_user, db=db
            )
            return user
        else:
            raise HTTPException(
                status_code=510, detail="Cannot update the role as admin"
            )
    user = create_new_user(input_obj=user, user_name=current_user, db=db)
    return user


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=UserVM,
)
async def update__user(
    user: UserVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    role = get_role(user.roleId, db=db)
    if (
        role.Code == Constants.RoleAdmin
        or role.Code == Constants.RoleDemoAdmin
    ):
        if (
            current_user_role == Constants.RoleAdmin
            or current_user_role == Constants.RoleDemoAdmin
        ):
            result = update_user(input=user, user=current_user, db=db)
            return result
        else:
            raise HTTPException(
                status_code=510, detail="Cannot update the role as admin"
            )
    else:
        user = update_user(input=user, user=current_user, db=db)
        return user


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[UserVM]
)
async def read_all(db: Session = Depends(get_db)):
    users = list_user(db=db)
    return paginate(users)


@router.get(
    "/active", dependencies=[Depends(JWTBearer())], response_model=Page[UserVM]
)
async def read_all_active(db: Session = Depends(get_db)):
    users = list_user_active(db=db)
    return paginate(users)


@router.get(
    "/get/{userId}", dependencies=[Depends(JWTBearer())], response_model=UserVM
)
async def get(userId: int, db: Session = Depends(get_db)):
    user = get_user_by_id(userId=userId, db=db)
    return user


@router.delete(
    "/delete/{userId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=UserVM,
)
async def delete(userId: int, db: Session = Depends(get_db)):
    users = delete_user(userId=userId, db=db)
    return users
