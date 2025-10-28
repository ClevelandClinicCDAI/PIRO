from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.hospital import (
    create_new_hospital,
    delete_hospital,
    get_hospital,
    list_hospital,
    list_hospital_active,
    update_hospital,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.hospital import HospitalVM, HospitalVMCreate, HospitalVMUpdate

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=HospitalVM,
)
async def create_hospital(
    hospital: HospitalVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_hospital(input=hospital, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=HospitalVM,
)
async def update__hospital(
    hospital: HospitalVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_hospital(input=hospital, user=current_user, db=db)
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[HospitalVM],
)
async def read_hospital_all(db: Session = Depends(get_db)):
    hospitals = list_hospital(db=db)
    return paginate(hospitals)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[HospitalVM],
)
async def read_hospital_all_active(db: Session = Depends(get_db)):
    hospitals = list_hospital_active(db=db)
    return paginate(hospitals)


@router.get(
    "/get/{hospitalId}",
    dependencies=[Depends(JWTBearer())],
    response_model=HospitalVM,
)
async def get(hospitalId: int, db: Session = Depends(get_db)):
    hospital = get_hospital(hospitalId=hospitalId, db=db)
    return hospital


@router.delete(
    "/delete/{hospitalId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=HospitalVM,
)
async def delete(hospitalId: int, db: Session = Depends(get_db)):
    hospital = delete_hospital(hospitalId=hospitalId, db=db)
    return hospital
