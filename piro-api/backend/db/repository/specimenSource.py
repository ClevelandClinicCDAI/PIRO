from db.models.SpecimenSource import SpecimenSource
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.specimenSource import (
    SpecimenSourceVMCreate,
    SpecimenSourceVMUpdate,
)


def create_new_specimenSource(
    input: SpecimenSourceVMCreate, user: str, db: Session
):
    specimenSource = SpecimenSource(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        RCPScore=input.score,
        IsActive=True,
        CreateBy=user,
    )
    db.add(specimenSource)
    db.commit()
    db.refresh(specimenSource)
    return specimenSource


def update_specimenSource(
    input: SpecimenSourceVMUpdate, user: str, db: Session
):
    specimenSource = (
        db.query(SpecimenSource)
        .filter(SpecimenSource.SpecimenSourceId == input.specimenSourceId)
        .first()
    )
    if specimenSource is not None:
        specimenSource.ShortName = input.display
        specimenSource.Code = input.code
        specimenSource.Description = input.description
        specimenSource.DataLabReference = input.reference
        specimenSource.RCPScore = input.score
        specimenSource.IsActive = True
        specimenSource.UpdatedBy = user
        db.commit()
    else:
        raise DataException("SpecimenSource does not exist")
    return specimenSource


def list_specimenSource(db: Session):
    specimenSource = (
        db.query(SpecimenSource).order_by(asc(SpecimenSource.ShortName)).all()
    )
    return specimenSource


def list_specimenSource_active(db: Session):
    specimenSource = (
        db.query(SpecimenSource)
        .filter(SpecimenSource.IsActive == True)  # noqa
        .order_by(asc(SpecimenSource.ShortName))
        .all()
    )  # noqa
    return specimenSource


def get_specimenSource(specimenSourceId: int, db: Session):
    specimentSource = (
        db.query(SpecimenSource)
        .filter(SpecimenSource.SpecimenSourceId == specimenSourceId)
        .first()
    )
    if specimentSource is None:
        raise DataException("SpecimenSource does not exist")
    return specimentSource


def delete_specimenSource(specimenSourceId: int, db: Session):
    specimenSource = (
        db.query(SpecimenSource)
        .filter(SpecimenSource.SpecimenSourceId == specimenSourceId)
        .filter(SpecimenSource.IsActive == True)  # noqa
        .first()
    )  # noqa
    if specimenSource is not None:
        specimenSource.IsActive = False
        db.commit()
    else:
        raise DataException("SpecimenSource does not exist")
    return specimenSource
