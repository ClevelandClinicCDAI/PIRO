from typing import Annotated, Callable, Union
from logger import logger
from core.config import settings
from core.constants import Constants
from core.ldap_auth import user_group, user_login, user_display_name
from core.oauth_auth import (
    extract_identity,
    user_group as oauth_user_group,
    verify_oauth_token,
)
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
from viewmodel.tokens import OAuthLoginVM, UserLoginVM

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


def _get_or_provision_user(
    nuid: str,
    resolve_names: Callable[[], dict],
    islog: bool,
    db: Session,
):
    """Shared user lookup + provisioning branch used by both auth paths.

    Encapsulates the "look up by NUID; if missing, create; if inactive,
    reject" logic that used to live inline in ``authenticate_user``.
    Behaviour (including the ``except Exception`` wrapping semantics) is
    preserved verbatim from the LDAP-only implementation.

    ``resolve_names`` is a zero-arg callable returning
    ``{"firstName": ..., "lastName": ...}``. Wrapping it in a callable
    defers name resolution to the provisioning branch only: the LDAP
    path avoids a redundant AD lookup when the user already exists.
    """
    credentials_active_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not active",
    )

    try:
        user = get_user_by_nuid(nuid=nuid, db=db)
        if not user:
            # If the user is not present in the database, create the user
            # account. If the user account is inactive, then DO NOT create
            # the new user account.
            message: str = "User not present in the system"
            logger.error(message)
            create_user_log(
                nuid,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.ACCOUNT.name,
                message,
                islog,
                db=db,
            )
            userCheck = check_user_active(nuid=nuid, db=db)
            # userCheck values, True: user active, False: user inactive,
            # None: User never created in database
            if userCheck is None:
                message = "User not active in the system"
                logger.error(message)
                create_user_log(
                    nuid,
                    -1,
                    -1,
                    Constants.StatusCode.E.name,
                    Constants.LoginTypeCode.ACCOUNT.name,
                    nuid,
                    islog,
                    db=db,
                )
                names = resolve_names()
                roleId = get_role_id(Constants.RoleUser, db=db)
                user = create_new_user_details(
                    nuid=nuid,
                    firstName=names["firstName"],
                    lastName=names["lastName"],
                    roleId=roleId,
                    user=nuid,
                    db=db,
                )
                message = f"User '{nuid}' created in the system."
                logger.info(message)
                create_user_log(
                    nuid,
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
                nuid,
                -1,
                -1,
                Constants.StatusCode.E.name,
                Constants.LoginTypeCode.AD.name,
                message,
                islog,
                db=db,
            )
            raise credentials_active_exception
        message = "User accessed from the PIRO database"
        logger.info(message)
        create_user_log(
            nuid,
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
            f"User authentication error for username '{nuid}'. Error: {e}"
        )
        logger.error(message)
        create_user_log(
            nuid,
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


def _authenticate_via_ldap(body: UserLoginVM, islog: bool, db: Session):
    """LDAP-backed authentication path (preserves original behaviour)."""
    username = body.username
    password = body.password

    credentials_invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    credentials_group_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not a part of the security group",
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

    def resolve_names() -> dict:
        return user_display_name(
            userName=username, password=password, islog=True, db=db
        )

    return _get_or_provision_user(username, resolve_names, islog, db)


def _authenticate_via_oauth(body: OAuthLoginVM, islog: bool, db: Session):
    """OAuth/OIDC-backed authentication path."""
    credentials_invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    credentials_group_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not a part of the security group",
    )

    claims = verify_oauth_token(id_token=body.id_token, islog=islog, db=db)
    if claims is None:
        raise credentials_invalid_exception

    identity = extract_identity(claims)
    nuid = identity["nuid"]
    if not nuid:
        message = (
            f"OAuth id_token missing required NUID claim "
            f"'{settings.OIDC_NUID_CLAIM}'."
        )
        logger.error(message)
        create_user_log(
            "",
            -1,
            -1,
            Constants.StatusCode.E.name,
            Constants.LoginTypeCode.OAUTH.name,
            message,
            islog,
            db=db,
        )
        raise credentials_invalid_exception

    if not oauth_user_group(claims=claims, nuid=nuid, islog=islog, db=db):
        raise credentials_group_exception

    def resolve_names() -> dict:
        return {
            "firstName": identity["firstName"],
            "lastName": identity["lastName"],
        }

    return _get_or_provision_user(nuid, resolve_names, islog, db)


def authenticate_user(
    credentials: Union[UserLoginVM, OAuthLoginVM],
    islog: bool,
    db: Session,
):
    """Dispatch authentication to the provider configured by AUTH_MODE."""
    if settings.AUTH_MODE == "OAUTH":
        if not isinstance(credentials, OAuthLoginVM):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Server configured for OAUTH; expected id_token "
                    "in request body."
                ),
            )
        return _authenticate_via_oauth(credentials, islog, db)

    if not isinstance(credentials, UserLoginVM):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Server configured for LDAP; expected username and "
                "password in request body."
            ),
        )
    return _authenticate_via_ldap(credentials, islog, db)


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
