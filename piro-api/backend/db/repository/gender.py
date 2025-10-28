from db.models.Gender import Gender
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.gender import GenderVMCreate, GenderVMUpdate


def create_new_gender(input: GenderVMCreate, user: str, db: Session):
    gender = Gender(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(gender)
    db.commit()
    db.refresh(gender)
    return gender


def update_gender(input: GenderVMUpdate, user: str, db: Session):
    gender = db.query(Gender).filter(Gender.GenderId == input.genderId).first()
    if gender is not None:
        gender.ShortName = input.display
        gender.Code = input.code
        gender.Description = input.description
        gender.DataLabReference = input.reference
        gender.IsActive = True
        gender.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Gender does not exist")
    return gender


def list_gender(db: Session):
    gender = db.query(Gender).order_by(asc(Gender.ShortName)).all()
    return gender


def list_gender_active(db: Session):
    gender = (
        db.query(Gender)
        .filter(Gender.IsActive == True)  # noqa
        .order_by(asc(Gender.ShortName))
        .all()
    )
    return gender


def get_gender(genderId: int, db: Session):
    gender = db.query(Gender).filter(Gender.GenderId == genderId).first()
    if gender is None:
        raise DataException("Gender does not exist")
    return gender


def delete_gender(genderId: int, db: Session):
    gender = (
        db.query(Gender)
        .filter(Gender.GenderId == genderId)
        .filter(Gender.IsActive == True)  # noqa
        .first()
    )  # noqa
    if gender is not None:
        gender.IsActive = False
        db.commit()
    else:
        raise DataException("Gender does not exist")
    return gender
