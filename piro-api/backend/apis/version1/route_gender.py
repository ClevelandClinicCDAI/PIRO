from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.gender import (
    create_new_gender,
    delete_gender,
    get_gender,
    list_gender,
    list_gender_active,
    update_gender,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.gender import (
    GenderVM,
    GenderVMCreate,
    GenderVMDropdown,
    GenderVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=GenderVM,
)
async def create_gender(
    gender: GenderVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_gender(input=gender, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=GenderVM,
)
async def update__gender(
    gender: GenderVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_gender(input=gender, user=current_user, db=db)
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[GenderVM]
)
async def read_gender_all(db: Session = Depends(get_db)):
    genders = list_gender(db=db)
    return paginate(genders)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[GenderVM],
)
async def read_gender_all_active(db: Session = Depends(get_db)):
    genders = list_gender_active(db=db)
    return paginate(genders)


@router.get(
    "/dropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[GenderVMDropdown],
)
async def read_gender_all_dropdown(db: Session = Depends(get_db)):
    genders = list_gender_active(db=db)
    return genders


@router.get(
    "/get/{genderId}",
    dependencies=[Depends(JWTBearer())],
    response_model=GenderVM,
)
async def get(genderId: int, db: Session = Depends(get_db)):
    gender = get_gender(genderId=genderId, db=db)
    return gender


@router.delete(
    "/delete/{genderId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=GenderVM,
)
async def delete(genderId: int, db: Session = Depends(get_db)):
    gender = delete_gender(genderId=genderId, db=db)
    return gender
