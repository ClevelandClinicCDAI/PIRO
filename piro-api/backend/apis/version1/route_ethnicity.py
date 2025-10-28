from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.ethnicity import (
    create_new_ethnicity,
    delete_ethnicity,
    get_ethnicity,
    list_ethnicity,
    list_ethnicity_active,
    update_ethnicity,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.ethnicity import (
    EthnicityVM,
    EthnicityVMCreate,
    EthnicityVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=EthnicityVM,
)
async def create_ethnicity(
    ethnicity: EthnicityVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_ethnicity(input=ethnicity, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=EthnicityVM,
)
async def update__ethnicity(
    ethnicity: EthnicityVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_ethnicity(input=ethnicity, user=current_user, db=db)
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[EthnicityVM],
)
async def read_ethnicity_all(db: Session = Depends(get_db)):
    ethnicitys = list_ethnicity(db=db)
    return paginate(ethnicitys)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[EthnicityVM],
)
async def read_ethnicity_all_active(db: Session = Depends(get_db)):
    ethnicitys = list_ethnicity_active(db=db)
    return paginate(ethnicitys)


@router.get(
    "/get/{ethnicityId}",
    dependencies=[Depends(JWTBearer())],
    response_model=EthnicityVM,
)
async def get(ethnicityId: int, db: Session = Depends(get_db)):
    ethnicity = get_ethnicity(ethnicityId=ethnicityId, db=db)
    return ethnicity


@router.delete(
    "/delete/{ethnicityId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=EthnicityVM,
)
async def delete(ethnicityId: int, db: Session = Depends(get_db)):
    ethnicity = delete_ethnicity(ethnicityId=ethnicityId, db=db)
    return ethnicity
