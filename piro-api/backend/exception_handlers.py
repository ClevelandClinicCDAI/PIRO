import sys
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
from logger import logger


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of
    FastAPI. This function will be called when client input is not valid.
    """
    # logger.debug("Our custom request_validation_exception_handler was called")
    body = await request.body()
    query_params = request.query_params._dict  # pylint: disable=protected-access
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
    # logger.debug("Our custom http_exception_handler was called")
    # host = getattr(getattr(request, "client", None), "host", None)
    # port = getattr(getattr(request, "client", None), "port", None)
    # url = f"{request.url.path}?{request.query_params}" if
    # request.query_params else request.url.path
    # exception_type, exception_value, exception_traceback = sys.exc_info()
    # exception_name = getattr(exception_type, "__name__", None)
    # logger.error(
    #     f'{host}:{port} - "{request.method} {url}" HTTP Server Error <{
    #     exception_name}: {exception_value}>'
    # )
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
    # logger.debug("Our custom unhandled_exception_handler was called")
    # host = getattr(getattr(request, "client", None), "host", None)
    # port = getattr(getattr(request, "client", None), "port", None)
    # url = f"{request.url.path}?{request.query_params}" if
    # request.query_params else request.url.path
    # exception_type, exception_value, exception_traceback = sys.exc_info()
    # exception_name = getattr(exception_type, "__name__", None)
    # logger.error(
    #     f'{host}:{port} - "{request.method} {url}" 500 Internal Server
    #     Error <{exception_name}: {exception_value}>'
    # )
    # logger.error(repr(traceback.print_stack()))
    # return PlainTextResponse(str(exc), status_code=500)
    # return PlainTextResponse(exception_value, status_code=500)
    await log_error(request, exc)
    return Response("Internal server error", status_code=550)


async def log_error(request: Request, exc: Exception):
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or
    RequestValidationErrors.
    """
    # logger.debug("Our custom unhandled_exception_handler was called")
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)
    logger.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error '
        f"<{exception_name}: {exception_value} : {str(exc)} : {exc.args}>"
    )
