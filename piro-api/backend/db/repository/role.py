from db.models.Role import Role
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.role import RoleVMCreate, RoleVMUpdate
from logger import logger


def create_new_role(input: RoleVMCreate, user: str, db: Session):
    role = Role(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        IsActive=True,
        CreateBy=user,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(input: RoleVMUpdate, user: str, db: Session):
    role = db.query(Role).filter(Role.RoleId == input.roleId).first()
    if role is not None:
        role.ShortName = input.display
        role.Code = input.code
        role.Description = input.description
        role.DataLabReference = input.reference
        role.IsActive = True
        role.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Role does not exist")
    return role


def list_role(db: Session):
    role = db.query(Role).order_by(asc(Role.ShortName)).all()
    return role


def list_role_active(db: Session):
    role = (
        db.query(Role)
        .filter(Role.IsActive == True)  # noqa
        .order_by(asc(Role.ShortName))
        .all()
    )
    return role


def get_role(roleId: int, db: Session):
    role = db.query(Role).filter(Role.RoleId == roleId).first()
    if role is None:
        raise DataException("Role does not exist")
    return role


def get_role_id(code: str, db: Session):
    role = db.query(Role).filter(Role.Code == code).first()
    if role is None:
        raise DataException("Role does not exist")
    return role.RoleId


def delete_role(roleId: int, db: Session):
    role = (
        db.query(Role)
        .filter(Role.RoleId == roleId)
        .filter(Role.IsActive == True)  # noqa
        .first()
    )
    if role is not None:
        role.IsActive = False
        db.commit()
    else:
        raise DataException("Role does not exist")
    return role


def ensure_role_exists(
    *,
    code: str,
    short_name: str,
    description: str,
    reference: str,
    user: str,
    db: Session,
):
    """
    Ensure a role with the given code exists and is active.

    If the role is missing, create it. If it exists but is inactive or has stale
    metadata, refresh it so it shows up in admin dropdowns.
    """
    role = db.query(Role).filter(Role.Code == code).first()

    if role is None:
        role = Role(
            ShortName=short_name,
            Code=code,
            Description=description,
            DataLabReference=reference,
            IsActive=True,
            CreateBy=user,
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        logger.info("Created missing role '%s'.", code)
        return role

    updated = False

    if not role.IsActive:
        role.IsActive = True
        updated = True

    if role.ShortName != short_name:
        role.ShortName = short_name
        updated = True

    if role.Description != description:
        role.Description = description
        updated = True

    if role.DataLabReference != reference:
        role.DataLabReference = reference
        updated = True

    if updated:
        role.UpdateBy = user
        db.commit()
        db.refresh(role)
        logger.info("Updated role '%s' to ensure it is active and current.", code)

    return role
