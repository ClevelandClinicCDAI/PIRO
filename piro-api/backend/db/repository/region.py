from db.models.Region import Region
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.region import RegionVMCreate, RegionVMUpdate


def create_new_region(input: RegionVMCreate, user: str, db: Session):
    region = Region(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def update_region(input: RegionVMUpdate, user: str, db: Session):
    region = db.query(Region).filter(Region.RegionId == input.regionId).first()
    if region is not None:
        region.ShortName = input.display
        region.Code = input.code
        region.Description = input.description
        region.DataLabReference = input.reference
        region.IsActive = True
        region.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Region does not exist")
    return region


def list_region(db: Session):
    region = db.query(Region).order_by(asc(Region.ShortName)).all()
    return region


def list_region_active(db: Session):
    region = (
        db.query(Region)
        .filter(Region.IsActive == True)  # noqa
        .order_by(asc(Region.ShortName))
        .all()
    )  # noqa
    return region


def get_region(regionId: int, db: Session):
    region = db.query(Region).filter(Region.RegionId == regionId).first()
    if region is None:
        raise DataException("Region does not exist")
    return region


def delete_region(regionId: int, db: Session):
    region = (
        db.query(Region)
        .filter(Region.RegionId == regionId)
        .filter(Region.IsActive == True)  # noqa
        .first()
    )
    if region is not None:
        region.IsActive = False
        db.commit()
    else:
        raise DataException("Region does not exist")
    return region
