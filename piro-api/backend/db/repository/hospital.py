from db.models.Hospital import Hospital
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.hospital import HospitalVMCreate, HospitalVMUpdate


def create_new_hospital(input: HospitalVMCreate, user: str, db: Session):
    hospital = Hospital(
        RegionId=input.regionId,
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def update_hospital(input: HospitalVMUpdate, user: str, db: Session):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.HospitalId == input.hospitalId)
        .first()
    )
    if hospital is not None:
        # hospital.RegionId = input.regionId
        hospital.ShortName = input.display
        hospital.Code = input.code
        hospital.Description = input.description
        hospital.DataLabReference = input.reference
        hospital.IsActive = True
        hospital.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Hospital does not exist")
    return hospital


def list_hospital(db: Session):
    hospital = db.query(Hospital).order_by(asc(Hospital.ShortName)).all()
    return hospital


def list_hospital_active(db: Session):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.IsActive == True)  # noqa
        .order_by(asc(Hospital.ShortName))
        .all()
    )  # noqa
    return hospital


def get_hospital(hospitalId: int, db: Session):
    hospital = (
        db.query(Hospital).filter(Hospital.HospitalId == hospitalId).first()
    )
    if hospital is None:
        raise DataException("Hospital does not exist")
    return hospital


def delete_hospital(hospitalId: int, db: Session):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.HospitalId == hospitalId)
        .filter(Hospital.IsActive == True)  # noqa
        .first()
    )  # noqa
    if hospital is not None:
        hospital.IsActive = False
        db.commit()
    else:
        raise DataException("Hospital does not exist")
    return hospital
