from datetime import datetime
from db.dict2Class import dict2Class
from db.models.Role import Role
from db.models.User import User
from db.models.UserRole import UserRole
from db.models.UserLog import UserLog
from exception.data_exception import DataException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from viewmodel.user import UserVMCreate, UserVMUpdate, UserVMUpdateProfile


def create_new_user(input_obj: UserVMCreate, user_name: str, db: Session):
    userNew = User(
        NUID=input_obj.nuid,
        FirstName=input_obj.firstName,
        LastName=input_obj.lastName,
        IsActive=True,
        CreateBy=user_name,
    )

    userRole = UserRole(
        RoleId=input_obj.roleId,
        IsActive=True,
        CreateBy=user_name,
        User=userNew,
    )
    db.add(userNew)
    db.add(userRole)
    db.commit()
    db.refresh(userNew)
    return get_user_by_id(userId=userNew.UserId, db=db)


def create_new_user_details(
    nuid: str,
    firstName: str,
    lastName: str,
    roleId: int,
    user: str,
    db: Session,
):
    userNew = User(
        NUID=nuid,
        FirstName=firstName,
        LastName=lastName,
        IsActive=True,
        CreateBy=user,
    )

    userRole = UserRole(
        RoleId=roleId, IsActive=True, CreateBy=user, User=userNew
    )
    db.add(userNew)
    db.add(userRole)
    db.commit()
    db.refresh(userNew)
    return get_user_by_id(userId=userNew.UserId, db=db)


def update_user(input: UserVMUpdate, user: str, db: Session):
    user = db.query(User).filter(User.UserId == input.userId).first()
    userRole = (
        db.query(UserRole).filter(UserRole.UserId == input.userId).first()
    )
    if user is None or userRole is None:
        raise DataException("User/Role does not exist")
    else:
        user.FirstName = input.firstName
        user.LastName = input.lastName
        user.NUID = input.nuid
        user.IsActive = True
        user.UpdatedBy = user
        userRole.RoleId = input.roleId
        db.commit()

    return get_user_by_id(userId=user.UserId, db=db)


def update_userprofile(
    input: UserVMUpdateProfile, userId: int, user: str, db: Session
):
    user = db.query(User).filter(User.UserId == userId).first()
    if user is None:
        raise DataException("User does not exist")
    else:
        user.FirstName = input.firstName
        user.LastName = input.lastName
        user.UpdatedBy = user
        db.commit()

    return get_user_by_id(userId=user.UserId, db=db)


def list_user(db: Session):
    users = []
    data = (
        db.query(User, UserRole, Role)
        .join(UserRole, User.UserId == UserRole.UserId)
        .join(Role, UserRole.RoleId == Role.RoleId)
        .filter()
        .order_by(asc(User.NUID))
        .all()
    )

    for user, userRole, role in data:
        result = dict2Class(
            {
                "UserId": user.UserId,
                "NUID": user.NUID,
                "FirstName": user.FirstName,
                "LastName": user.LastName,
                "Role": role.Code,
                "RoleId": userRole.RoleId,
                "IsActive": user.IsActive,
            }
        )
        users.append(result)
    return users


def list_user_active(db: Session):
    users = []
    data = (
        db.query(User, UserRole, Role)
        .join(UserRole, User.UserId == UserRole.UserId)
        .join(Role, UserRole.RoleId == Role.RoleId)
        .filter(User.IsActive == True)  # noqa: E712
        .order_by(asc(User.NUID))
        .all()
    )
    for user, userRole, role in data:
        result = dict2Class(
            {
                "UserId": user.UserId,
                "NUID": user.NUID,
                "FirstName": user.FirstName,
                "LastName": user.LastName,
                "Role": role.Code,
                "RoleId": userRole.RoleId,
                "IsActive": user.IsActive,
            }
        )
        users.append(result)
    return users


def get_user_by_nuid(nuid: str, db: Session):
    data = (
        db.query(User, UserRole, Role)
        .join(UserRole, User.UserId == UserRole.UserId)
        .join(Role, UserRole.RoleId == Role.RoleId)
        .filter(User.NUID == nuid)
        .order_by(desc(User.UserId))
    )

    for user, userRole, role in data:
        return dict2Class(
            {
                "UserId": user.UserId,
                "NUID": user.NUID,
                "FirstName": user.FirstName,
                "LastName": user.LastName,
                "Role": role.Code,
                "RoleId": userRole.RoleId,
                "IsActive": user.IsActive,
            }
        )


def check_user_active(nuid: str, db: Session):
    user = db.query(User).filter(User.NUID == nuid).first()

    if user is not None:
        return user.IsActive
    else:
        # Find inactive user account
        nuid = f"{nuid}[_]%"
        user = (
            db.query(User)
            .filter(User.NUID.ilike(nuid))
            .order_by(desc(User.UserId))
            .first()
        )
        if user is not None:
            return False
        else:
            return None


def get_user_by_id(userId: int, db: Session):
    data = (
        db.query(User, UserRole, Role)
        .join(UserRole, User.UserId == UserRole.UserId)
        .join(Role, UserRole.RoleId == Role.RoleId)
        .filter(User.UserId == userId)
    )

    for user, userRole, role in data:
        return dict2Class(
            {
                "UserId": user.UserId,
                "NUID": user.NUID,
                "FirstName": user.FirstName,
                "LastName": user.LastName,
                "Role": role.Code,
                "RoleId": userRole.RoleId,
                "IsActive": user.IsActive,
            }
        )

    raise DataException("User does not exist")


def delete_user(userId: int, db: Session):
    user = (
        db.query(User)
        .filter(User.UserId == userId)
        .filter(User.IsActive == True)  # noqa: E712
        .first()
    )
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    if user is not None:
        user.NUID = f"{user.NUID}_{time}"
        user.IsActive = False
        db.commit()
    else:
        raise DataException("User does not exist")
    return get_user_by_id(userId=user.UserId, db=db)


def create_user_log(
    nuid: str,
    userId: int,
    roleId: int,
    type: str,
    code: str,
    message: str,
    islog: bool,
    db: Session,
):
    """Insert a log entry into our database log table."""

    if not islog:
        return
    log = UserLog(
        NUID=nuid,
        UserId=userId,
        RoleId=roleId,
        Code=code,
        Type=type,
        Message=message,
        CreateBy=nuid,
    )
    db.add(log)
    db.commit()
