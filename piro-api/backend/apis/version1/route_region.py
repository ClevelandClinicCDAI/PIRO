from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.region import (
    create_new_region,
    delete_region,
    get_region,
    list_region,
    list_region_active,
    update_region,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.region import (
    RegionVM,
    RegionVMCreate,
    RegionVMDropdown,
    RegionVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RegionVM,
)
async def create_region(
    region: RegionVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_region(input=region, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RegionVM,
)
async def update__region(
    region: RegionVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_region(input=region, user=current_user, db=db)
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[RegionVM]
)
async def read_region_all(db: Session = Depends(get_db)):
    regions = list_region(db=db)
    return paginate(regions)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[RegionVM],
)
async def read_region_all_active(db: Session = Depends(get_db)):
    regions = list_region_active(db=db)
    return paginate(regions)


@router.get(
    "/dropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[RegionVMDropdown],
)
async def read_region_all_dropdown(db: Session = Depends(get_db)):
    regions = list_region_active(db=db)
    return regions


@router.get(
    "/get/{regionId}",
    dependencies=[Depends(JWTBearer())],
    response_model=RegionVM,
)
async def get(regionId: int, db: Session = Depends(get_db)):
    region = get_region(regionId=regionId, db=db)
    return region


@router.delete(
    "/delete/{regionId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RegionVM,
)
async def delete(regionId: int, db: Session = Depends(get_db)):
    region = delete_region(regionId=regionId, db=db)
    return region
