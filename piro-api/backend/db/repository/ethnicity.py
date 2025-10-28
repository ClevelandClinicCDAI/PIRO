from db.models.Ethnicity import Ethnicity
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.ethnicity import EthnicityVMCreate, EthnicityVMUpdate


def create_new_ethnicity(input: EthnicityVMCreate, user: str, db: Session):
    ethnicity = Ethnicity(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(ethnicity)
    db.commit()
    db.refresh(ethnicity)
    return ethnicity


def update_ethnicity(input: EthnicityVMUpdate, user: str, db: Session):
    ethnicity = (
        db.query(Ethnicity)
        .filter(Ethnicity.EthnicityId == input.ethnicityId)
        .first()
    )
    if ethnicity is not None:
        ethnicity.ShortName = input.display
        ethnicity.Code = input.code
        ethnicity.Description = input.description
        ethnicity.DataLabReference = input.reference
        ethnicity.IsActive = True
        ethnicity.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Ethnicity does not exist")
    return ethnicity


def list_ethnicity(db: Session):
    ethnicity = db.query(Ethnicity).order_by(asc(Ethnicity.ShortName)).all()
    return ethnicity


def list_ethnicity_active(db: Session):
    ethnicity = (
        db.query(Ethnicity)
        .filter(Ethnicity.IsActive == True)  # noqa
        .order_by(asc(Ethnicity.ShortName))
        .all()
    )  # noqa
    return ethnicity


def get_ethnicity(ethnicityId: int, db: Session):
    ethnicity = (
        db.query(Ethnicity)
        .filter(Ethnicity.EthnicityId == ethnicityId)
        .first()
    )
    if ethnicity is None:
        raise DataException("Ethnicity does not exist")
    return ethnicity


def delete_ethnicity(ethnicityId: int, db: Session):
    ethnicity = (
        db.query(Ethnicity)
        .filter(Ethnicity.EthnicityId == ethnicityId)
        .filter(Ethnicity.IsActive == True)  # noqa
        .first()
    )  # noqa
    if ethnicity is not None:
        ethnicity.IsActive = False
        db.commit()
    else:
        raise DataException("Ethnicity does not exist")
    return ethnicity
