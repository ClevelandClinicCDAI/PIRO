from db.models.Role import Role
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.role import RoleVMCreate, RoleVMUpdate


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
