from typing import Annotated
from logger import logger
from core.config import settings
from core.constants import Constants
from core.ldap_auth import user_group, user_login, user_display_name
from core.security_token import (
    decode_access_nuid_token,
    decode_access_token,
    decode_access_userid_token,
    decode_access_isattest_token,
)
from db.repository.role import get_role_id
from db.repository.user import (
    check_user_active,
    create_new_user_details,
    get_user_by_nuid,
    create_user_log,
)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl="token", authorizationUrl="token"
)


def get_current_user_nuid(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token=token)
        if payload is None:
            raise credentials_exception from None
    except HTTPException:
        raise credentials_exception from HTTPException
    nuid = decode_access_nuid_token(token)
    if nuid is None:
        raise credentials_exception from None
    return nuid


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token=token)
        if payload is None:
            raise credentials_exception from None
    except HTTPException:
        raise credentials_exception from HTTPException
    userId = decode_access_userid_token(token)
    if userId is None:
        raise credentials_exception from None
    return userId


def get_current_user_attest(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token=token)
        if payload is None:
            raise credentials_exception
    except HTTPException:
        raise credentials_exception from HTTPException
    isAttest = decode_access_isattest_token(token)
    if isAttest is None:
        raise credentials_exception
    return isAttest


def authenticate_user(username: str, password: str, islog: bool, db: Session):
    credentials_invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    credentials_group_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not a part of the security group",
    )

    credentials_active_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not active",
    )

    if (
        settings.ACCESS_TOKEN_TEST_USER == ""
        or username not in settings.ACCESS_TOKEN_TEST_USER
    ):
        if (
            user_login(
                userName=username, password=password, islog=islog, db=db
            )
            is False
        ):
            message = "Could not validate credentials"
            logger.error(message)
            create_user_log(
                username,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.CREDENTIAL.name,
                message,
                islog,
                db=db,
            )
            raise credentials_invalid_exception
        if (
            user_group(
                userName=username, password=password, islog=islog, db=db
            )
            is False
        ):
            message = "User not a part of the security group"
            logger.error(message)
            create_user_log(
                username,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.AD.name,
                message,
                islog,
                db=db,
            )
            raise credentials_group_exception

    try:
        user = get_user_by_nuid(nuid=username, db=db)
        if not user:
            # If the user is not present in the database, create the user
            # account. If the user account is inactive, then DO NOT create
            # the new user account.
            message: str = "User not present in the system"
            logger.error(message)
            create_user_log(
                username,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.ACCOUNT.name,
                message,
                islog,
                db=db,
            )
            userCheck = check_user_active(nuid=username, db=db)
            # userCheck values, True: user active, False: user inactive,
            # None: User never created in database
            if userCheck is None:
                message = "User not active in the system"
                logger.error(message)
                create_user_log(
                    username,
                    -1,
                    -1,
                    Constants.StatusCode.E.name,
                    Constants.LoginTypeCode.ACCOUNT.name,
                    username,
                    islog,
                    db=db,
                )
                userLdap = user_display_name(
                    userName=username, password=password, islog=True, db=db
                )
                roleId = get_role_id(Constants.RoleUser, db=db)
                user = create_new_user_details(
                    nuid=username,
                    firstName=userLdap["firstName"],
                    lastName=userLdap["lastName"],
                    roleId=roleId,
                    user=username,
                    db=db,
                )
                message = f"User '{username}' created in the system."
                logger.info(message)
                create_user_log(
                    username,
                    -1,
                    -1,
                    Constants.StatusCode.S.name,
                    Constants.LoginTypeCode.ACCOUNT.name,
                    message,
                    islog,
                    db=db,
                )
                return user
            else:
                return False
        elif user.IsActive is False:
            message = "User inactive"
            logger.error(message)
            create_user_log(
                username,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.AD.name,
                message,
                islog,
                db=db,
            )
            raise credentials_active_exception
        # user = get_user_by_id(userId=user.UserId, db=db)
        message = "User accessed from the PIRO database"
        logger.info(message)
        create_user_log(
            username,
            -1,
            -1,
            Constants.StatusCode.S.name,
            Constants.LoginTypeCode.ACCOUNT.name,
            message,
            islog,
            db=db,
        )
        return user
    except Exception as e:
        message: str = (
            f"User authentication error for username '{username}'. Error: {e}"
        )
        logger.error(message)
        create_user_log(
            username,
            -1,
            -1,
            Constants.StatusCode.E.name,
            Constants.LoginTypeCode.ACCOUNT.name,
            message,
            islog,
            db=db,
        )
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
        raise credentials_exception from e


def get_current_user_role(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    payload = decode_access_token(token=token, checkExpiry=True)

    if payload is None:
        return None
    else:
        return payload.get("role")


def get_current_user_name(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token=token, checkExpiry=True)
    if payload is None:
        return None
    else:
        return payload.get("name")
