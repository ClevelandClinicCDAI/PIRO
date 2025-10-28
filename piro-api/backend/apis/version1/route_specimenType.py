from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.specimenType import (
    create_new_specimenType,
    delete_specimenType,
    get_specimenType,
    list_specimenType,
    list_specimenType_active,
    update_specimenType,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.specimenType import (
    SpecimenTypeVM,
    SpecimenTypeVMCreate,
    SpecimenTypeVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenTypeVM,
)
async def create_specimenType(
    specimenType: SpecimenTypeVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_specimenType(
        input=specimenType, user=current_user, db=db
    )
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenTypeVM,
)
async def update__specimenType(
    specimenType: SpecimenTypeVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_specimenType(input=specimenType, user=current_user, db=db)
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SpecimenTypeVM],
)
async def read_specimenType_all(db: Session = Depends(get_db)):
    specimenTypes = list_specimenType(db=db)
    return paginate(specimenTypes)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SpecimenTypeVM],
)
async def read_specimenType_all_active(db: Session = Depends(get_db)):
    specimenTypes = list_specimenType_active(db=db)
    return paginate(specimenTypes)


@router.get(
    "/get/{specimenTypeId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SpecimenTypeVM,
)
async def get(specimenTypeId: int, db: Session = Depends(get_db)):
    specimenType = get_specimenType(specimenTypeId=specimenTypeId, db=db)
    return specimenType


@router.delete(
    "/delete/{specimenTypeId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenTypeVM,
)
async def delete(specimenTypeId: int, db: Session = Depends(get_db)):
    specimenType = delete_specimenType(specimenTypeId=specimenTypeId, db=db)
    return specimenType
