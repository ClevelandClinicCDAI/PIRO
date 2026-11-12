from typing import Union

from fastapi import Request
from fastapi.exception_handlers import (
    http_exception_handler as _http_exception_handler,
)
from fastapi.exception_handlers import (
    request_validation_exception_handler as requestValidationExceptionHandler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from piro_logger import logger


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of
    FastAPI. This function will be called when client input is not valid.
    """
    body = await request.body()
    query_params = (
        request.query_params._dict
    )  # pylint: disable=protected-access
    detail = {
        "errors": exc.errors(),
        "body": body.decode(),
        "query_params": query_params,
    }
    logger.error(detail)
    return await requestValidationExceptionHandler(request, exc)


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> Union[JSONResponse, Response]:
    """
    This is a wrapper to the default HTTPException handler of FastAPI.
    This function will be called when a HTTPException is explicitly raised.
    """
    await log_error(request, exc)
    return await _http_exception_handler(request, exc)


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or
    RequestValidationErrors.
    """
    await log_error(request, exc)
    return PlainTextResponse("Internal server error", status_code=550)


async def log_error(request: Request, exc: Exception):
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or
    RequestValidationErrors.
    """
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    logger.opt(exception=exc).error(
        '{}:{} - "{} {}" request failed ({})',
        host,
        port,
        request.method,
        request.url.path,
        type(exc).__name__,
    )
