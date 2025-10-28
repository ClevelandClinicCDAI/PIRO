from datetime import datetime, timedelta

from core.config import settings
import jwt
from logger import logger


def create_access_token(
    userId: int, nuid: str, role: str, name: str, isAttest: bool = False
):
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"userId": 0, "nuid": "", "role": "", "name": ""}
    data["userId"] = userId
    data["nuid"] = nuid
    data["role"] = role
    data["name"] = name
    data["isAttest"] = isAttest
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str, checkExpiry: bool = True):
    payload = jwt.decode(
        token,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithms=settings.ACCESS_TOKEN_ALGORITHM,
    )

    if checkExpiry:
        expiry_time = payload["exp"]
        current_time = datetime.now()
        current_timestamp = int(round(current_time.timestamp()))
        return payload if expiry_time >= current_timestamp else None
    else:
        return payload


def decode_access_userid_token(token: str):
    payload = decode_access_token(token=token)

    userId: str = payload.get("userId")

    return userId


def decode_access_nuid_token(token: str, checkExpiry: bool = True):
    payload = decode_access_token(token=token, checkExpiry=checkExpiry)

    nuid: str = payload.get("nuid")

    return nuid


def decode_access_role_token(token: str):
    payload = decode_access_token(token=token)

    role: str = payload.get("role")

    return role


def decode_access_isattest_token(token: str) -> bool:
    payload = decode_access_token(token=token)

    isAttest: bool = payload.get("isAttest")

    return isAttest


def refresh_jwt(jwtoken: str, checkExpiry: bool) -> bool:
    try:
        payload = decode_access_token(jwtoken, checkExpiry)
    except Exception as e:
        logger.error(
            f"Please see log for error messaging: " f"{type(e), e, e.args}"
        )
        return None
    if payload:
        return create_access_token(
            payload.get("userId"),
            payload.get("nuid"),
            payload.get("role"),
            payload.get("name"),
            payload.get("isAttest"),
        )
    else:
        return None
