import json
from datetime import datetime
from decimal import Decimal
from typing import Any, NoReturn

import pytest
from apis.external_api.admin import issue_key, revoke_key, set_client_active
from apis.external_api.app import create_external_app, mount_external_api
from apis.external_api.config import ExternalAPISettings
from apis.external_api.models import audits, cases, keys, leases, orders, usage
from apis.external_api.service import ExternalService
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import insert, select, update

from tests.external_api.types import ApiFixture

PATH: str = "/linked-orders/search"


def seed(api: ApiFixture) -> None:
    """Populate duplicate cases and representative linked-order fixtures."""
    with api["engine"].begin() as connection:
        connection.execute(
            insert(cases),
            [
                {"CaseId": 1, "CaseNumber": "S26-1"},
                {"CaseId": 2, "CaseNumber": "S26-1"},
                {"CaseId": 3, "CaseNumber": "S26-EMPTY"},
                {"CaseId": 4, "CaseNumber": "UNREQUESTED"},
            ],
        )
        values: list[dict[str, Any]] = []
        for identifier, case_id, name, external, description in [
            (1, 1, "PD-L1", None, None),
            (2, 2, None, "pd-l1 assay", None),
            (3, 2, None, None, "Test PD-l1 result"),
            (4, 2, "OTHER", None, None),
            (5, None, "PD-L1", None, None),
            (6, 4, "PD-L1", None, None),
        ]:
            values.append(
                {
                    "LinkedOrderId": identifier,
                    "CaseId": case_id,
                    "ComponentName": name,
                    "ComponentExternalName": external,
                    "ProcedureDesc": description,
                    "DefaultUnit": None,
                    "OrdValue": "positive",
                    "OrdNumValue": Decimal("12.34000"),
                }
            )
        connection.execute(insert(orders), values)


def search(
    api: ApiFixture, body: dict[str, Any] | None = None, **kwargs: Any
) -> Response:
    """Submit a request with the fixture application key."""
    return api["client"].post(
        PATH,
        json=body or {"case_numbers": ["S26-1"]},
        headers=api["headers"],
        **kwargs,
    )


def test_complete_batch_joins_all_cases_and_filters_each_description(
    api: ApiFixture,
) -> None:
    """Verify complete batch joins all cases and filters each description."""
    seed(api)
    response = search(
        api,
        {
            "case_numbers": [" S26-1 ", "S26-1", "S26-EMPTY", "MISSING"],
            "test_type": " Pd-L1 ",
        },
    )
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    assert body["record_count"] == len(body["data"]) == 3
    assert {item["CaseNumber"] for item in body["data"]} == {"S26-1"}
    assert all(item["OrdNumValue"] == "12.34000" for item in body["data"])
    assert all(item["DefaultUnit"] is None for item in body["data"])
    assert set(body["data"][0]) == {
        "CaseNumber",
        "ComponentName",
        "ComponentExternalName",
        "ProcedureDesc",
        "DefaultUnit",
        "OrdValue",
        "OrdNumValue",
    }
    assert body["cases"] == [
        {"CaseNumber": "S26-1", "status": "matched", "record_count": 3},
        {
            "CaseNumber": "S26-EMPTY",
            "status": "no_matching_orders",
            "record_count": 0,
        },
        {
            "CaseNumber": "MISSING",
            "status": "case_not_found",
            "record_count": 0,
        },
    ]
    assert response.headers["x-request-id"] == body["request_id"]
    assert response.headers["cache-control"] == "no-store"
    with api["engine"].connect() as connection:
        audit = (
            connection.execute(
                select(audits).where(audits.c.RequestId == body["request_id"])
            )
            .mappings()
            .one()
        )
        assert audit.ClientId == api["client_id"]
        assert audit.RecordCount == 3
        assert json.loads(audit.CaseNumbersJson) == [
            "S26-1",
            "S26-EMPTY",
            "MISSING",
        ]
        assert json.loads(audit.CaseResultsJson) == body["cases"]
        assert connection.scalar(select(usage.c.ReturnedRecords)) == 3
        assert connection.scalar(select(leases.c.RequestId)) is None


def test_omitted_filter_and_duplicate_records_are_preserved(
    api: ApiFixture,
) -> None:
    """Verify omitted filter and duplicate records are preserved."""
    seed(api)
    with api["engine"].begin() as connection:
        source = dict(
            connection.execute(
                select(orders).where(orders.c.LinkedOrderId == 1)
            )
            .mappings()
            .one()
        )
        source["LinkedOrderId"] = 7
        connection.execute(insert(orders).values(**source))
        connection.execute(update(orders).values(OrdNumValue=None))
    response = search(api)
    assert response.status_code == 200
    assert response.json()["record_count"] == 5
    assert all(row["OrdNumValue"] is None for row in response.json()["data"])


@pytest.mark.parametrize("needle", ["%", "_", "[", "\\", "' OR 1=1 --"])
def test_literal_search_does_not_expand_wildcards_or_sql(
    api: ApiFixture, needle: str
) -> None:
    """Verify literal search does not expand wildcards or sql."""
    with api["engine"].begin() as connection:
        connection.execute(insert(cases).values(CaseId=1, CaseNumber="S26-1"))
        connection.execute(
            insert(orders),
            [
                {
                    "LinkedOrderId": 1,
                    "CaseId": 1,
                    "ComponentName": "prefix" + needle + "suffix",
                },
                {
                    "LinkedOrderId": 2,
                    "CaseId": 1,
                    "ComponentName": "unrelated",
                },
            ],
        )
    response = search(api, {"case_numbers": ["S26-1"], "test_type": needle})
    assert response.status_code == 200
    assert response.json()["record_count"] == 1
    assert (
        response.json()["data"][0]["ComponentName"]
        == "prefix" + needle + "suffix"
    )


def test_case_number_injection_does_not_select_other_cases(
    api: ApiFixture,
) -> None:
    """Verify case number injection does not select other cases."""
    seed(api)
    response = search(api, {"case_numbers": ["S26-1') OR 1=1 --"]})
    assert response.status_code == 200
    assert response.json()["record_count"] == 0


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"case_numbers": []},
        {"case_numbers": ["  "]},
        {"case_numbers": [123]},
        {"case_numbers": ["x" * 101]},
        {"case_numbers": ["a"], "test_type": " "},
        {"case_numbers": ["a"], "test_type": 12},
        {"case_numbers": ["a"], "test_type": "x" * 201},
        {"case_numbers": ["a"], "unknown": True},
    ],
)
def test_invalid_input_does_not_return_data_and_releases_lease(
    api: ApiFixture, body: dict[str, Any] | None
) -> None:
    """Verify invalid input does not return data and releases lease."""
    response = api["client"].post(PATH, json=body, headers=api["headers"])
    assert response.status_code == 422
    assert "data" not in response.json()
    with api["engine"].connect() as connection:
        assert connection.scalar(select(leases.c.RequestId)) is None
        assert connection.scalar(select(usage.c.ReturnedRecords)) == 0


def test_request_body_limit_including_streamed_body(api: ApiFixture) -> None:
    """Verify request body limit including streamed body."""
    api["config"].max_body_bytes = 1024
    response = api["client"].post(
        PATH,
        content=iter([b'{"case_numbers": ["', b"x" * 2048, b'"]}']),
        headers={**api["headers"], "Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"


def test_batch_and_record_limits_never_return_partial_results(
    api: ApiFixture,
) -> None:
    """Verify batch and record limits never return partial results."""
    seed(api)
    api["config"].max_cases = 1
    response = search(api, {"case_numbers": ["S26-1", "S26-EMPTY"]})
    assert response.status_code == 422
    api["config"].max_records = 3
    response = search(api)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "result_limit_exceeded"
    assert "data" not in response.json()
    with api["engine"].connect() as connection:
        assert connection.scalar(select(usage.c.ReturnedRecords)) == 0
        assert connection.scalar(select(leases.c.RequestId)) is None


def test_quota_counts_successful_retries_and_rejects_whole_batch(
    api: ApiFixture,
) -> None:
    """Verify quota counts successful retries and rejects whole batch."""
    seed(api)
    api["config"].daily_records = 5
    assert search(api).status_code == 200
    response = search(api)
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "daily_quota_exceeded"
    assert int(response.headers["retry-after"]) > 0
    assert "data" not in response.json()
    with api["engine"].connect() as connection:
        assert connection.scalar(select(usage.c.ReturnedRecords)) == 4


def test_rate_limit(api: ApiFixture) -> None:
    """Verify rate limit."""
    api["config"].requests_per_minute = 1
    assert search(api).status_code == 200
    response = search(api)
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limit_exceeded"


@pytest.mark.parametrize(
    "supplied", [None, "invalid", "piro_" + "a" * 32 + "_" + "b" * 43]
)
def test_invalid_keys_and_ui_tokens_are_rejected_and_audited(
    api: ApiFixture, supplied: str | None
) -> None:
    """Verify invalid keys and ui tokens are rejected and audited."""
    headers = {"Authorization": "Bearer not-a-piro-session"}
    if supplied:
        headers["X-API-Key"] = supplied
    response = api["client"].post(
        PATH, json={"case_numbers": ["a"]}, headers=headers
    )
    assert response.status_code == 401
    assert "www-authenticate" in response.headers
    with api["engine"].connect() as connection:
        audit = (
            connection.execute(
                select(audits).where(
                    audits.c.RequestId == response.json()["request_id"]
                )
            )
            .mappings()
            .one()
        )
        assert audit.StatusCode == 401
        assert audit.ClientId is None


def test_key_hash_rotation_revocation_and_disable(api: ApiFixture) -> None:
    """Verify key hash rotation revocation and disable."""
    credential: dict[str, str] = api["credential"]
    with api["engine"].connect() as connection:
        row = connection.execute(select(keys)).mappings().one()
        assert row.SecretHash != credential["api_key"]
        assert len(row.SecretHash) == 64
        assert credential["api_key"] not in str(row)
    new_key = issue_key(api["engine"], api["client_id"], "pytest")
    assert search(api).status_code == 200
    revoke_key(api["engine"], credential["key_id"], "pytest")
    assert search(api).status_code == 401
    api["headers"] = {"X-API-Key": new_key["api_key"]}
    assert search(api).status_code == 200
    set_client_active(api["engine"], api["client_id"], "pytest", False)
    assert search(api).status_code == 403


def test_expired_key(api: ApiFixture) -> None:
    """Verify expired key."""

    with api["engine"].begin() as connection:
        connection.execute(update(keys).values(ExpiresAt=datetime(2000, 1, 1)))
    assert search(api).status_code == 401


def test_database_and_audit_failures_never_masquerade_as_empty_success(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify database and audit failures never masquerade as empty success."""
    from sqlalchemy.exc import OperationalError

    service: ExternalService = api["app"].state.service

    def fail(*_args: Any) -> NoReturn:
        """Simulate a database or audit failure without returning data."""
        raise OperationalError(
            "sensitive SQL", {}, Exception("sensitive value")
        )

    monkeypatch.setattr(service, "search", fail)
    response = search(api)
    assert response.status_code == 503
    assert "sensitive" not in response.text
    assert "data" not in response.json()
    monkeypatch.setattr(service, "record_failure", fail)
    response = search(api)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "audit_unavailable"


def test_success_is_withheld_if_audit_insert_fails(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify success is withheld if audit insert fails."""
    seed(api)

    def fail(*_args: Any, **_kwargs: Any) -> NoReturn:
        """Simulate a database or audit failure without returning data."""
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("apis.external_api.service.insert_request_audit", fail)
    response = search(api)
    assert response.status_code == 503
    assert "data" not in response.json()
    with api["engine"].connect() as connection:
        assert connection.scalar(select(usage.c.ReturnedRecords)) == 0


def test_openapi_is_separate_and_disabled_mode_has_no_db_dependency() -> None:
    """Verify openapi is separate and disabled mode has no db dependency."""
    app = create_external_app(
        ExternalAPISettings(enabled=False, _env_file=None)
    )
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert (
            client.post(PATH, json={"case_numbers": ["a"]}).status_code == 404
        )
    assert app.state.service is None


@pytest.mark.parametrize("mode", ["LDAP", "OAUTH"])
def test_real_ui_middleware_and_token_validation_are_isolated(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    """Verify real ui middleware and token validation are isolated."""
    from core.auth_bearer import JWTBearer
    from core.config import settings
    from core.security_token import create_access_token
    from middleware import log_request_middleware

    monkeypatch.setattr(settings, "AUTH_MODE", mode)
    monkeypatch.setattr(
        settings,
        "ACCESS_TOKEN_SECRET_KEY",
        "test-only-secret-key-for-piro-jwt-validation",
    )
    monkeypatch.setattr(settings, "ACCESS_TOKEN_ALGORITHM", "HS256")
    parent: FastAPI = FastAPI()
    parent.middleware("http")(log_request_middleware)
    mount_external_api(parent, api["config"], api["engine"])

    @parent.get("/internal", dependencies=[Depends(JWTBearer())])
    def internal() -> dict[str, bool]:
        """Expose a protected UI route for authentication isolation checks."""
        return {"ok": True}

    with TestClient(parent) as client:
        headers = {
            **api["headers"],
            "Authorization": "Bearer deliberately-invalid",
        }
        response = client.post(
            "/external/v1" + PATH,
            json={"case_numbers": ["a"]},
            headers=headers,
        )
        assert response.status_code == 200
        assert "refreshtoken" not in response.headers
        assert (
            client.get("/internal", headers=api["headers"]).status_code == 403
        )
        token = create_access_token(1, "test", "ADMIN", "Test")
        internal_response = client.get(
            "/internal", headers={"Authorization": f"Bearer {token}"}
        )
        assert internal_response.status_code == 200
        assert "refreshtoken" in internal_response.headers
        assert (
            client.post(
                "/external/v1" + PATH,
                json={"case_numbers": ["a"]},
                headers={"Authorization": f"Bearer {token}"},
            ).status_code
            == 401
        )
        assert (
            "/external/v1/linked-orders/search"
            not in client.get("/openapi.json").json()["paths"]
        )
        schema = client.get("/external/v1/openapi.json").json()
        assert list(schema["paths"]) == [PATH]
        assert (
            schema["components"]["securitySchemes"]["IntegrationApiKey"][
                "name"
            ]
            == "X-API-Key"
        )


def test_proxy_root_path_keeps_external_credentials_out_of_ui_middleware(
    api: ApiFixture,
) -> None:
    """Verify proxy root path keeps external credentials out of ui
    middleware."""
    from middleware import log_request_middleware

    parent: FastAPI = FastAPI(root_path="/api")
    parent.middleware("http")(log_request_middleware)
    mount_external_api(parent, api["config"], api["engine"])
    with TestClient(parent) as client:
        response = client.post(
            "/api/external/v1" + PATH,
            json={"case_numbers": ["a"]},
            headers={**api["headers"], "Authorization": "Bearer invalid"},
        )
        assert response.status_code == 200
        assert "refreshtoken" not in response.headers


def test_production_application_factory_mounts_external_app(
    api: ApiFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Do not connect to the deployment database or run its startup hooks.
    """Verify production application factory mounts external app."""
    import apis.external_api.app as external_app
    from core.config import settings

    monkeypatch.setattr(settings, "PROJECT_NAME", "PIRO Test")
    monkeypatch.setattr(settings, "PROJECT_VERSION", "1.0.0")
    monkeypatch.setattr(settings, "DATABASE", "MSSQL")
    monkeypatch.setattr(settings, "AUTH_MODE", "LDAP")
    monkeypatch.setattr(
        external_app,
        "mount_external_api",
        lambda parent: mount_external_api(
            parent, api["config"], api["engine"]
        ),
    )
    import main

    app = main.start_application()
    with TestClient(app) as client:
        response = client.post(
            "/external/v1" + PATH,
            json={"case_numbers": ["a"]},
            headers=api["headers"],
        )
        assert response.status_code == 200
        assert app.state.external_api.state.service.engine is api["engine"]


def test_openapi_requires_all_seven_nullable_record_fields(
    api: ApiFixture,
) -> None:
    """Verify openapi requires all seven nullable record fields."""
    schema = api["client"].get("/openapi.json").json()
    assert schema["openapi"] == "3.0.3"
    record = schema["components"]["schemas"]["LinkedOrder"]
    assert set(record["required"]) == {
        "CaseNumber",
        "ComponentName",
        "ComponentExternalName",
        "ProcedureDesc",
        "DefaultUnit",
        "OrdValue",
        "OrdNumValue",
    }
    assert record["properties"]["OrdNumValue"]["type"] == "string"
    assert record["properties"]["OrdNumValue"]["nullable"] is True
