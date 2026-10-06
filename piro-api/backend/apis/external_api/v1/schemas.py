from typing import Literal

from pydantic import BaseModel, Field, StrictStr, constr, validator


class SearchRequest(BaseModel):
    """The stable v1 case lookup and optional literal test filter."""

    case_numbers: list[constr(strict=True, min_length=1, max_length=100)] = (  # type: ignore[reportInvalidTypeForm]  # noqa:E501
        Field(
            ...,
            min_items=1,
            max_items=500,
            description="Exact case numbers, trimmed and deduplicated; deployment limit defaults to 100.",  # noqa:E501
        )
    )
    test_type: constr(strict=True, min_length=1, max_length=200) | None = (  # type: ignore[reportInvalidTypeForm]  # noqa:E501
        Field(
            None,
            description="Optional literal, case-insensitive substring of any of the three test descriptions.",  # noqa:E501
        )
    )

    @validator("case_numbers")
    def normalize_cases(cls, values: list[str]) -> list[str]:
        """Trim and deduplicate exact submitted case numbers."""
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            value = value.strip()
            if not value or any(ord(char) < 32 for char in value):
                raise ValueError(
                    "Case numbers must be nonblank and contain no control characters."  # noqa:E501
                )
            # Case matching follows the source database collation.
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    @validator("test_type")
    def normalize_test_type(cls, value: str | None) -> str | None:
        """Normalize the optional literal filter and reject control characters."""
        if value is not None:
            value = value.strip()
            if not value or any(ord(char) < 32 for char in value):
                raise ValueError(
                    "test_type must be nonblank and contain no control characters."  # noqa:E501
                )
        return value

    class Config:
        """Reject undeclared request fields."""

        extra: str = "forbid"


class LinkedOrder(BaseModel):
    """The seven-field external record contract, independent of ORM models."""

    CaseNumber: StrictStr
    ComponentName: StrictStr | None = Field(..., nullable=True)
    ComponentExternalName: StrictStr | None = Field(..., nullable=True)
    ProcedureDesc: StrictStr | None = Field(..., nullable=True)
    DefaultUnit: StrictStr | None = Field(..., nullable=True)
    OrdValue: StrictStr | None = Field(..., nullable=True)
    OrdNumValue: StrictStr | None = Field(
        ...,
        nullable=True,
        description="Exact decimal string with five fractional digits; never a floating-point number.",  # noqa:E501
    )


CaseStatus = Literal["matched", "no_matching_orders", "case_not_found"]


class CaseResult(BaseModel):
    """Summarize matching results for one submitted case number."""

    CaseNumber: StrictStr
    status: CaseStatus
    record_count: int


class SearchResponse(BaseModel):
    """Return a complete batch with per-case outcomes and a request ID."""

    request_id: str
    data: list[LinkedOrder]
    record_count: int
    cases: list[CaseResult]


class ErrorDetail(BaseModel):
    """Describe an actionable public failure without internal details."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """The versioned public error envelope."""

    request_id: str
    error: ErrorDetail
