import http
import time
from datetime import datetime

from core.security_token import decode_access_nuid_token, refresh_jwt
from exception_handlers import log_error
from fastapi import Request, status
from fastapi.responses import PlainTextResponse
from logger import logger


async def log_request_middleware(request: Request, call_next):
    """
    This middleware will log all requests and their processing time.
    E.g. log:
    0.0.0.0:1234 - GET /ping 200 OK 1.00ms
    """
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path.lower()
    )
    start_time = time.time()

    try:
        nuid: str = ""
        access_token: str = ""
        autheader = request.headers.get("Authorization")
        if autheader is not None and autheader != "Bearer null":
            access_token_bearer = autheader.split()
            if len(access_token_bearer) > 1:
                access_token = access_token_bearer[1]
                nuid = decode_access_nuid_token(access_token, False)
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}"
        host = getattr(getattr(request, "client", None), "host", None)
        port = getattr(getattr(request, "client", None), "port", None)
        try:
            status_phrase = http.HTTPStatus(response.status_code).phrase
        except ValueError:
            status_phrase = ""
        logger.info(
            f'{datetime.now()} {nuid} {host}:{port} - "{request.method} {url}" '
            f"{response.status_code} {status_phrase} {formatted_process_time}ms"
        )
        if access_token != "":
            refreshToken = refresh_jwt(jwtoken=access_token, checkExpiry=False)

            if refreshToken is not None and not (
                ("/isvalid" in url)
                or ("/login" in url)
                or ("/lastdataupdated" in url)
            ):
                response.headers["access-control-expose-headers"] = (
                    "Refreshtoken"
                )
                response.headers["Refreshtoken"] = refreshToken
        return response
    except Exception as exc:
        logger.error(f"Error! Code: {type(exc).__name__}, Message, {str(exc)}")
        await log_error(request, exc)

        if (
            type(exc).__name__ == "JWTError"
            or type(exc).__name__ == "ExpiredSignatureError"
        ):
            return PlainTextResponse(
                str(exc), status_code=status.HTTP_401_UNAUTHORIZED
            )
        elif (
            type(exc).__name__ == "DataException"
            or type(exc).__name__ == "CustomException"
        ):
            return PlainTextResponse(str(exc), status_code=510)
        else:
            return PlainTextResponse(
                "Internal server error. Please contact server administrator",
                status_code=500,
            )
