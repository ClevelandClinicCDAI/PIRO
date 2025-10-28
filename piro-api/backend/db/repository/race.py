from db.models.Race import Race
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.race import RaceVMCreate, RaceVMUpdate


def create_new_race(input: RaceVMCreate, user: str, db: Session):
    race = Race(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(race)
    db.commit()
    db.refresh(race)
    return race


def update_race(input: RaceVMUpdate, user: str, db: Session):
    race = db.query(Race).filter(Race.RaceId == input.raceId).first()
    if race is not None:
        race.ShortName = input.display
        race.Code = input.code
        race.Description = input.description
        race.DataLabReference = input.reference
        race.IsActive = True
        race.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Race does not exist")
    return race


def list_race(db: Session):
    race = db.query(Race).order_by(asc(Race.ShortName)).all()
    return race


def list_race_active(db: Session):
    race = (
        db.query(Race)
        .filter(Race.IsActive == True)  # noqa
        .order_by(asc(Race.ShortName))
        .all()
    )  # noqa
    return race


def get_race(raceId: int, db: Session):
    race = db.query(Race).filter(Race.RaceId == raceId).first()
    if race is None:
        raise DataException("Race does not exist")
    return race


def delete_race(raceId: int, db: Session):
    race = (
        db.query(Race)
        .filter(Race.RaceId == raceId)
        .filter(Race.IsActive == True)  # noqa
        .first()
    )  # noqa
    if race is not None:
        race.IsActive = False
        db.commit()
    else:
        raise DataException("Race does not exist")
    return race
