from typing import Annotated, Union

from core.auth_bearer import JWTBearer
from core.oauth_auth import get_end_session_endpoint
from core.security_token import create_access_token
from core.security_user import (
    authenticate_user,
    get_current_user_name,
    get_current_user_nuid,
    get_current_user_role,
    get_current_user_id,
)
from db.session import get_db
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from logger import logger
from sqlalchemy.orm import Session
from viewmodel.tokens import LogoutResponseVM, OAuthLoginVM, Token, UserLoginVM
from viewmodel.user import UserAuthVM, UserDetailsVM
from core.constants import Constants
from viewmodel.userAttestation import UserAttestationVM
from db.repository.userAttestation import (
    create_new_attestation,
    get_attestation,
    get_is_attested,
)
from db.repository.user import create_user_log
from core.config import settings

# from core.security_user import get_current_user_details
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    credentials: Union[UserLoginVM, OAuthLoginVM] = Body(...),
    db: Session = Depends(get_db),
):
    logger.info("Attempting to authenticate!")

    user = authenticate_user(credentials, credentials.islog, db)
    if not user:
        logger.info("No user found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, User does not exist",
        )

    else:
        logger.info("User authenticated!")

    isAttest = get_is_attested(userId=user.UserId, db=db)
    message: str = f"User Attest - {isAttest}"
    logger.info(message)
    create_user_log(
        user.NUID,
        -1,
        -1,
        Constants.StatusCode.S.name,
        Constants.LoginTypeCode.ATTEST.name,
        message,
        credentials.islog,
        db=db,
    )
    expiry_minutes = (
        settings.SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES
        if user.Role == Constants.RoleSlideRoom
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        user.UserId,
        user.NUID,
        user.Role,
        f"{user.LastName}, {user.FirstName}",
        isAttest,
        expiry_minutes,
    )
    message: str = "Token created"
    logger.info(message)
    create_user_log(
        user.NUID,
        -1,
        -1,
        Constants.StatusCode.S.name,
        Constants.LoginTypeCode.TOKEN.name,
        message,
        credentials.islog,
        db=db,
    )

    # response.set_cookie(
    #     key="access_token", value=f"Bearer {access_token}", httponly=True
    # )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/isvalid", dependencies=[Depends(JWTBearer())], response_model=UserAuthVM
)
async def get_is_valid(
    current_user_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    if current_user_role is None:
        return {"IsAuth": False, "Role": ""}
    else:
        return {"IsAuth": True, "Role": current_user_role}


@router.get(
    "/user", dependencies=[Depends(JWTBearer())], response_model=UserDetailsVM
)
async def get_user(
    current_user_name: Annotated[str, Depends(get_current_user_name)],
    current_user_nuid: Annotated[str, Depends(get_current_user_nuid)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    if get_current_user_name is None:
        return {"IsAuth": False, "Name": "", "Nuid": "", "Role": ""}
    else:
        return {
            "IsAuth": True,
            "Name": current_user_name,
            "Nuid": current_user_nuid,
            "Role": current_user_role,
        }


@router.post(
    "/attest",
    dependencies=[Depends(JWTBearer([]))],
    response_model=UserAttestationVM,
)
async def get_attest(
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = get_attestation(int(current_userid), db)
    return result


@router.get("/saveattest", dependencies=[Depends(JWTBearer())])
async def saveAttest(
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = create_new_attestation(int(current_userid), current_user, db)
    return result


@router.post(
    "/logout",
    dependencies=[Depends(JWTBearer())],
    response_model=LogoutResponseVM,
)
async def logout(
    current_user_nuid: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    """End the caller's PIRO session.

    The API is stateless (JWT-based), so "logging out" means:

    * Record the logout event in ``UserLog`` for audit.
    * If configured for OAuth, return the IdP's RP-initiated logout URL
      so the client can optionally end the shared IdP session (SLO).

    The SPA is responsible for discarding the PIRO JWT locally in
    every case.
    """
    message = f"User '{current_user_nuid}' logged out."
    logger.info(message)
    try:
        user_id_int = int(current_user_id) if current_user_id else -1
    except (TypeError, ValueError):
        user_id_int = -1
    create_user_log(
        current_user_nuid,
        user_id_int,
        -1,
        Constants.StatusCode.S.name,
        Constants.LoginTypeCode.TOKEN.name,
        message,
        True,
        db=db,
    )

    end_session_url = None
    if settings.AUTH_MODE == "OAUTH":
        end_session_url = get_end_session_endpoint()

    return {"end_session_url": end_session_url}
