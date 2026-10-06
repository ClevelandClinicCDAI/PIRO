"""Independent HTTP boundary for versioned external APIs."""

import logging
from time import monotonic
from uuid import uuid4

from db.engine import create_database_engine
from fastapi import FastAPI, Request, Security
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import ExternalAPISettings
from .context import RequestContext
from .errors import ExternalAPIError
from .security import Principal, key_id
from .service import ExternalService
from .v1.schemas import ErrorResponse, SearchRequest, SearchResponse

log = logging.getLogger("piro.external_api")
api_key_header = APIKeyHeader(
    name="X-API-Key", auto_error=False, scheme_name="IntegrationApiKey"
)


def error_response(
    error: ExternalAPIError, context: RequestContext
) -> JSONResponse:
    """Build the stable public error envelope and retry headers."""
    context["error_code"] = error.code
    headers: dict[str, str] = {
        "Cache-Control": "no-store",
        "X-Request-ID": context["request_id"],
    }
    if error.retry_after is not None:
        headers["Retry-After"] = str(error.retry_after)
    if error.status == 401:
        headers["WWW-Authenticate"] = 'ApiKey realm="piro-external"'
    return JSONResponse(
        {
            "request_id": context["request_id"],
            "error": {"code": error.code, "message": error.message},
        },
        status_code=error.status,
        headers=headers,
    )


class ExternalBoundary:
    """Keep external request handling independent of UI authentication."""

    def __init__(
        self,
        app: ASGIApp,
        config: ExternalAPISettings,
        service: ExternalService | None,
    ) -> None:
        """Bind the application, limits, and optional enabled service."""
        self.app: ASGIApp = app
        self.config: ExternalAPISettings = config
        self.service: ExternalService | None = service

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Bound requests and withhold responses until auditing completes."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        context: RequestContext = {
            "request_id": uuid4().hex,
            "started": monotonic(),
            "method": scope["method"][:10],
            "route": scope["path"][:200],
            "source_address": (
                str(scope.get("client", ("",))[0])[:100]
                if scope.get("client")
                else None
            ),
        }
        scope.setdefault("state", {})["external_context"] = context
        if not self.config.enabled:
            return await error_response(
                ExternalAPIError(
                    404,
                    "external_api_disabled",
                    "The external API is not enabled.",
                ),
                context,
            )(scope, receive, send)
        path: str = scope["path"].removeprefix(scope.get("root_path", ""))
        metadata_request: bool = scope["method"] == "GET" and path in {
            "/docs",
            "/docs/oauth2-redirect",
            "/openapi.json",
        }
        messages: list[Message] = []

        async def capture(message: Message) -> None:
            """Buffer a response message until the audit outcome is known."""
            messages.append(message)

        try:
            # Buffer only a bounded request, including requests with no
            # Content-Length or a misleading/chunked body.
            body: bytearray = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > self.config.max_body_bytes:
                    raise ExternalAPIError(
                        413,
                        "request_too_large",
                        "Request body exceeds the size limit.",
                    )
                if not message.get("more_body", False):
                    break
            consumed: bool = False

            async def replay() -> Message:
                """Replay the validated request body once to the
                application."""
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {
                        "type": "http.request",
                        "body": bytes(body),
                        "more_body": False,
                    }
                return await receive()

            await self.app(scope, replay, capture)
        except Exception as exc:
            messages = []
            if isinstance(exc, ExternalAPIError):
                error = exc
            elif isinstance(exc, SQLAlchemyError):
                error = ExternalAPIError(
                    503,
                    "database_unavailable",
                    "Database request failed; retry the complete batch.",
                    5,
                )
            else:
                error = ExternalAPIError(
                    500,
                    "internal_error",
                    "Request failed; retry the complete batch.",
                )
            # Exception text/SQL parameters may contain credentials or clinical data.  # noqa:E501
            log.error(
                "external_request_failed request_id=%s exception_type=%s",
                context["request_id"],
                type(exc).__name__,
            )
            await error_response(error, context)(scope, receive, capture)

        status: int = next(
            message["status"]
            for message in messages
            if message["type"] == "http.response.start"
        )
        if not metadata_request and not context.get("audited"):
            try:
                if self.service is None:
                    raise ValueError("Service is not initialized.")
                await run_in_threadpool(
                    self.service.record_failure,
                    context,
                    status,
                    context.get("error_code", "http_error"),
                )
            except Exception as exc:
                log.error(
                    "external_audit_failed request_id=%s exception_type=%s",
                    context["request_id"],
                    type(exc).__name__,
                )
                messages = []
                status = 503
                await error_response(
                    ExternalAPIError(
                        503,
                        "audit_unavailable",
                        "Access could not be audited; retry the complete batch.",  # noqa:E501
                        5,
                    ),
                    context,
                )(scope, receive, capture)
        for message in messages:
            if message["type"] == "http.response.start":
                headers: list[tuple[bytes, bytes]] = [
                    (key, value)
                    for key, value in message.get("headers", [])
                    if key.lower() not in {b"x-request-id", b"cache-control"}
                ]
                message["headers"] = headers + [
                    (b"x-request-id", context["request_id"].encode("ascii")),
                    (b"cache-control", b"no-store"),
                ]
            await send(message)
        if not metadata_request:
            log.info(
                "external_request request_id=%s status=%s elapsed_ms=%s",
                context["request_id"],
                status,
                int((monotonic() - context["started"]) * 1000),
            )


def create_external_app(
    config: ExternalAPISettings | None = None, engine: Engine | None = None
) -> FastAPI:
    """Create the independent v1 application, schema, and security boundary."""
    config = config or ExternalAPISettings()
    service: ExternalService | None = (
        ExternalService(
            engine
            or create_database_engine(
                query_timeout_seconds=config.query_timeout_seconds
            ),
            config,
        )
        if config.enabled
        else None
    )
    app: FastAPI = FastAPI(
        title="PIRO External API",
        version="1.0.0",
        debug=False,
        description="Application-authenticated, complete linked-order batches. Coordinate calls with PIRO ETL.",  # noqa:E501
        redoc_url=None,
    )
    # Pydantic v1 emits nullable in OpenAPI 3.0 form; publish that dialect
    # explicitly so generated clients correctly accept required null fields.
    app.openapi_version = "3.0.3"
    app.state.service = service
    app.add_middleware(ExternalBoundary, config=config, service=service)

    @app.exception_handler(ExternalAPIError)
    async def handle_external(
        request: Request, exc: ExternalAPIError
    ) -> JSONResponse:
        """Translate an expected service error to the external contract."""
        return error_response(exc, request.state.external_context)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(
        request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        # Do not echo request bodies, submitted identifiers, or credentials.
        """Return a validation failure without echoing submitted values."""
        return error_response(
            ExternalAPIError(
                422,
                "invalid_request",
                "Invalid request. Check case_numbers, test_type, and the v1 schema.",  # noqa:E501
            ),
            request.state.external_context,
        )

    @app.exception_handler(HTTPException)
    async def handle_http(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Translate route and method failures to the external contract."""
        return error_response(
            ExternalAPIError(
                exc.status_code,
                "http_error",
                "The requested route or method is unavailable.",
            ),
            request.state.external_context,
        )

    def require_key(
        request: Request, supplied_key: str | None = Security(api_key_header)
    ) -> Principal:
        """Authenticate and admit a request using only its application key."""
        if service is None:
            raise ExternalAPIError(
                500,
                "internal_error",
                "Service is not initialized.",
            )
        context: RequestContext = request.state.external_context
        context["key_id"] = key_id(supplied_key)
        principal: Principal = service.authenticate(supplied_key)
        context["principal"] = principal
        service.admit(principal, context["request_id"])
        return principal

    @app.post(
        "/linked-orders/search",
        response_model=SearchResponse,
        operation_id="searchLinkedOrdersV1",
        tags=["Linked orders"],
        responses={
            code: {"model": ErrorResponse}
            for code in (401, 403, 413, 422, 429, 500, 503)
        },
    )
    def search(
        body: SearchRequest,
        request: Request,
        _principal: Principal = Security(require_key),
    ) -> Response:
        """Serialize the complete result before committing its audit and
        quota."""
        if service is None:
            raise ExternalAPIError(
                500,
                "internal_error",
                "Service is not initialized.",
            )
        context: RequestContext = request.state.external_context
        context["case_numbers"] = body.case_numbers
        context["test_type"] = body.test_type
        result: SearchResponse = service.search(body, context["request_id"])
        # Serialize before committing quota/audit; no partially serialized
        # result can be recorded as a successful response.
        response: Response = Response(
            result.json(), media_type="application/json"
        )
        service.complete(context, result)
        return response

    return app


def mount_external_api(
    app: FastAPI,
    config: ExternalAPISettings | None = None,
    engine: Engine | None = None,
) -> None:
    """Mount v1 without merging its schema or dependencies into UI routes."""
    external: FastAPI = create_external_app(config=config, engine=engine)
    app.mount("/external/v1", external, name="external-v1")
    app.state.external_api = external
