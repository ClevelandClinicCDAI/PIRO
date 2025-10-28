from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.race import (
    create_new_race,
    delete_race,
    get_race,
    list_race,
    list_race_active,
    update_race,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.race import RaceVM, RaceVMCreate, RaceVMUpdate

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RaceVM,
)
async def create_race(
    race: RaceVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_race(input=race, user=current_user, db=db)
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RaceVM,
)
async def update__race(
    race: RaceVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_race(input=race, user=current_user, db=db)
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[RaceVM]
)
async def read_race_all(db: Session = Depends(get_db)):
    races = list_race(db=db)
    return paginate(races)


@router.get(
    "/active", dependencies=[Depends(JWTBearer())], response_model=Page[RaceVM]
)
async def read_race_all_active(db: Session = Depends(get_db)):
    races = list_race_active(db=db)
    return paginate(races)


@router.get(
    "/get/{raceId}", dependencies=[Depends(JWTBearer())], response_model=RaceVM
)
async def get(raceId: int, db: Session = Depends(get_db)):
    race = get_race(raceId=raceId, db=db)
    return race


@router.delete(
    "/delete/{raceId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=RaceVM,
)
async def delete(raceId: int, db: Session = Depends(get_db)):
    race = delete_race(raceId=raceId, db=db)
    return race
