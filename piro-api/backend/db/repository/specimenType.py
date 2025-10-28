from db.models.SpecimenType import SpecimenType
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.specimenType import SpecimenTypeVMCreate, SpecimenTypeVMUpdate


def create_new_specimenType(
    input: SpecimenTypeVMCreate, user: str, db: Session
):
    specimenType = SpecimenType(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        Category=input.category,
        IsActive=True,
        CreateBy=user,
    )
    db.add(specimenType)
    db.commit()
    db.refresh(specimenType)
    return specimenType


def update_specimenType(input: SpecimenTypeVMUpdate, user: str, db: Session):
    specimenType = (
        db.query(SpecimenType)
        .filter(SpecimenType.SpecimenTypeId == input.specimenTypeId)
        .first()
    )
    if specimenType is not None:
        specimenType.ShortName = input.display
        specimenType.Code = input.code
        specimenType.Description = input.description
        specimenType.DataLabReference = input.reference
        specimenType.IsActive = True
        specimenType.UpdatedBy = user
        db.commit()
    else:
        raise DataException("SpecimenType does not exist")
    return specimenType


def list_specimenType(db: Session):
    specimenType = (
        db.query(SpecimenType).order_by(asc(SpecimenType.ShortName)).all()
    )
    return specimenType


def list_specimenType_active(db: Session):
    specimenType = (
        db.query(SpecimenType)
        .filter(SpecimenType.IsActive == True)  # noqa
        .order_by(asc(SpecimenType.ShortName))
        .all()
    )  # noqa
    return specimenType


def get_specimenType(specimenTypeId: int, db: Session):
    specimenType = (
        db.query(SpecimenType)
        .filter(SpecimenType.SpecimenTypeId == specimenTypeId)
        .first()
    )
    if specimenType is None:
        raise DataException("SpecimenType does not exist")
    return specimenType


def delete_specimenType(specimenTypeId: int, db: Session):
    specimenType = (
        db.query(SpecimenType)
        .filter(SpecimenType.SpecimenTypeId == specimenTypeId)
        .filter(SpecimenType.IsActive == True)  # noqa
        .first()
    )  # noqa
    if specimenType is not None:
        specimenType.IsActive = False
        db.commit()
    else:
        raise DataException("SpecimenType does not exist")
    return specimenType
