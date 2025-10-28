from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.specimenSource import (
    create_new_specimenSource,
    delete_specimenSource,
    get_specimenSource,
    list_specimenSource,
    list_specimenSource_active,
    update_specimenSource,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.specimenSource import (
    SpecimenSourceVM,
    SpecimenSourceVMCreate,
    SpecimenSourceVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenSourceVM,
)
async def create_specimenSource(
    specimenSource: SpecimenSourceVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_specimenSource(
        input=specimenSource, user=current_user, db=db
    )
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenSourceVM,
)
async def update__specimenSource(
    specimenSource: SpecimenSourceVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_specimenSource(
        input=specimenSource, user=current_user, db=db
    )
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SpecimenSourceVM],
)
async def read_specimenSource_all(db: Session = Depends(get_db)):
    specimenSources = list_specimenSource(db=db)
    return paginate(specimenSources)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SpecimenSourceVM],
)
async def read_specimenSource_all_active(db: Session = Depends(get_db)):
    specimenSources = list_specimenSource_active(db=db)
    return paginate(specimenSources)


@router.get(
    "/get/{specimenSourceId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SpecimenSourceVM,
)
async def get(specimenSourceId: int, db: Session = Depends(get_db)):
    specimenSource = get_specimenSource(
        specimenSourceId=specimenSourceId, db=db
    )
    return specimenSource


@router.delete(
    "/delete/{specimenSourceId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=SpecimenSourceVM,
)
async def delete(specimenSourceId: int, db: Session = Depends(get_db)):
    specimenSource = delete_specimenSource(
        specimenSourceId=specimenSourceId, db=db
    )
    return specimenSource
