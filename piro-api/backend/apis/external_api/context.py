"""Request metadata shared by the HTTP boundary and audit service."""

from typing import NotRequired, TypedDict

from .security import Principal


class RequestContext(TypedDict):
    """Track verified identity, request details, and durable audit
    completion."""

    request_id: str
    started: float
    method: NotRequired[str]
    route: NotRequired[str]
    source_address: NotRequired[str | None]
    principal: NotRequired[Principal]
    key_id: NotRequired[str | None]
    case_numbers: NotRequired[list[str]]
    test_type: NotRequired[str | None]
    error_code: NotRequired[str]
    audited: NotRequired[bool]
