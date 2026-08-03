"""Unit tests for :mod:`core.oauth_auth`.

Tests focus on the pure/mockable branches of the OIDC provider module:
token verification error paths, claim extraction, and group-check
semantics. The IdP itself is never contacted — ``PyJWKClient``,
``requests.get``, and ``jwt.decode`` are all monkey-patched.
"""

import types
from unittest.mock import Mock

import jwt as pyjwt
import pytest
import requests

from core import oauth_auth
from core.config import settings


def _mock_db() -> Mock:
    """Return a mock DB session. All tests here pass ``islog=False`` so
    ``create_user_log`` short-circuits before touching it, which lets the
    tests avoid the sqlite fixture path in :mod:`tests.conftest`."""

    return Mock(name="db_session")


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _reset_module_caches():
    """Clear cached JWKS client and discovery doc between tests."""

    oauth_auth._jwks_client = None
    oauth_auth._discovery_document = None
    yield
    oauth_auth._jwks_client = None
    oauth_auth._discovery_document = None


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Override the parent conftest's DB-bootstrap fixture.

    The parent fixture creates a sqlite file at a hard-coded path and
    populates it from sample-data JSON — none of that is needed here
    because these tests only exercise pure functions with mocked I/O.
    """

    yield


@pytest.fixture
def issuer_configured(monkeypatch):
    """Set the minimum config required for `verify_oauth_token` to run."""

    monkeypatch.setattr(
        settings, "OIDC_ISSUER", "https://idp.example.com/tenant"
    )
    monkeypatch.setattr(settings, "OIDC_AUDIENCE", "piro-api")
    monkeypatch.setattr(
        settings, "OIDC_JWKS_URL", "https://idp.example.com/tenant/jwks"
    )
    monkeypatch.setattr(settings, "OIDC_ALGORITHMS", "RS256")
    monkeypatch.setattr(settings, "OIDC_CLOCK_SKEW_SECONDS", 60)
    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "preferred_username")


@pytest.fixture
def patch_jwks_client(monkeypatch):
    """Replace the JWKS client factory with a benign stub."""

    stub_key = types.SimpleNamespace(key="not-a-real-key")
    stub_client = types.SimpleNamespace(
        get_signing_key_from_jwt=Mock(return_value=stub_key)
    )
    monkeypatch.setattr(
        oauth_auth,
        "_get_jwks_client",
        lambda: stub_client,
    )
    return stub_client


# --------------------------------------------------------------------------- #
# verify_oauth_token                                                          #
# --------------------------------------------------------------------------- #


def test_verify_oauth_token_missing_issuer_returns_none(monkeypatch):
    """No configured issuer -> refuses to validate."""

    monkeypatch.setattr(settings, "OIDC_ISSUER", None)
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_jwks_key_lookup_fails(
    issuer_configured, monkeypatch
):
    """Failure to resolve the signing key returns None (no exception)."""

    def raise_boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        oauth_auth,
        "_get_jwks_client",
        raise_boom,
    )
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_expired_returns_none(
    issuer_configured, patch_jwks_client, monkeypatch
):
    monkeypatch.setattr(
        pyjwt, "decode", Mock(side_effect=pyjwt.ExpiredSignatureError())
    )
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_wrong_issuer_returns_none(
    issuer_configured, patch_jwks_client, monkeypatch
):
    monkeypatch.setattr(
        pyjwt, "decode", Mock(side_effect=pyjwt.InvalidIssuerError())
    )
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_wrong_audience_returns_none(
    issuer_configured, patch_jwks_client, monkeypatch
):
    monkeypatch.setattr(
        pyjwt, "decode", Mock(side_effect=pyjwt.InvalidAudienceError())
    )
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_generic_invalid_returns_none(
    issuer_configured, patch_jwks_client, monkeypatch
):
    monkeypatch.setattr(
        pyjwt,
        "decode",
        Mock(side_effect=pyjwt.InvalidTokenError("bad signature")),
    )
    db = _mock_db()
    assert oauth_auth.verify_oauth_token("any", islog=False, db=db) is None


def test_verify_oauth_token_success_returns_claims(
    issuer_configured, patch_jwks_client, monkeypatch
):
    """Happy path: valid token -> claims dict is returned unchanged."""

    claims = {
        "preferred_username": "jdoe",
        "iss": "https://idp.example.com/tenant",
        "aud": "piro-api",
        "groups": ["Group-A"],
    }
    monkeypatch.setattr(pyjwt, "decode", Mock(return_value=claims))
    db = _mock_db()
    result = oauth_auth.verify_oauth_token("any", islog=False, db=db)
    assert result == claims


def test_verify_oauth_token_skips_audience_when_unset(
    issuer_configured, patch_jwks_client, monkeypatch
):
    """When OIDC_AUDIENCE is empty, `verify_aud` is disabled."""

    monkeypatch.setattr(settings, "OIDC_AUDIENCE", "")
    decode = Mock(return_value={"sub": "x"})
    monkeypatch.setattr(pyjwt, "decode", decode)
    db = _mock_db()
    oauth_auth.verify_oauth_token("any", islog=False, db=db)
    kwargs = decode.call_args.kwargs
    assert "audience" not in kwargs
    assert kwargs.get("options") == {"verify_aud": False}


# --------------------------------------------------------------------------- #
# extract_identity                                                            #
# --------------------------------------------------------------------------- #


def test_extract_identity_uses_configured_claims(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "preferred_username")
    monkeypatch.setattr(settings, "OIDC_GIVEN_NAME_CLAIM", "given_name")
    monkeypatch.setattr(settings, "OIDC_FAMILY_NAME_CLAIM", "family_name")
    result = oauth_auth.extract_identity(
        {
            "preferred_username": "jdoe",
            "given_name": "Jane",
            "family_name": "Doe",
        }
    )
    assert result == {"nuid": "jdoe", "firstName": "Jane", "lastName": "Doe"}


def test_extract_identity_falls_back_to_name_when_split_missing(monkeypatch):
    """When given/family aren't present, split `name` on whitespace."""

    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "preferred_username")
    monkeypatch.setattr(settings, "OIDC_GIVEN_NAME_CLAIM", "given_name")
    monkeypatch.setattr(settings, "OIDC_FAMILY_NAME_CLAIM", "family_name")
    result = oauth_auth.extract_identity(
        {"preferred_username": "jdoe", "name": "Jane Doe"}
    )
    assert result == {"nuid": "jdoe", "firstName": "Jane", "lastName": "Doe"}


def test_extract_identity_missing_everything_returns_empty(monkeypatch):
    """All-empty claims -> empty strings (never None: DB has NOT NULL)."""

    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "preferred_username")
    result = oauth_auth.extract_identity({})
    assert result == {"nuid": "", "firstName": "", "lastName": ""}


def test_extract_identity_honors_custom_nuid_claim(monkeypatch):
    """Different IdPs put the login at different claim names."""

    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "upn")
    result = oauth_auth.extract_identity(
        {
            "upn": "jdoe@corp.example",
            "given_name": "Jane",
            "family_name": "Doe",
        }
    )
    assert result["nuid"] == "jdoe@corp.example"


def test_extract_identity_single_word_name_leaves_last_empty(monkeypatch):
    """Mononym in the `name` claim: firstName set, lastName stays empty."""

    monkeypatch.setattr(settings, "OIDC_NUID_CLAIM", "preferred_username")
    monkeypatch.setattr(settings, "OIDC_GIVEN_NAME_CLAIM", "given_name")
    monkeypatch.setattr(settings, "OIDC_FAMILY_NAME_CLAIM", "family_name")
    result = oauth_auth.extract_identity(
        {"preferred_username": "prince", "name": "Prince"}
    )
    assert result == {"nuid": "prince", "firstName": "Prince", "lastName": ""}


# --------------------------------------------------------------------------- #
# user_group                                                                  #
# --------------------------------------------------------------------------- #


def test_user_group_disabled_when_allowed_empty(monkeypatch):
    """Empty allowed list -> check is disabled, any user passes."""

    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert oauth_auth.user_group({}, nuid="jdoe", islog=False, db=db) is True


def test_user_group_list_match(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A,Group-B")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"groups": ["Group-X", "Group-B"]},
            nuid="jdoe",
            islog=False,
            db=db,
        )
        is True
    )


def test_user_group_list_no_match(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"groups": ["Group-X", "Group-Y"]},
            nuid="jdoe",
            islog=False,
            db=db,
        )
        is False
    )


def test_user_group_scalar_string_group(monkeypatch):
    """Some IdPs emit a single group as a string, not a list."""

    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"groups": "Group-A"}, nuid="jdoe", islog=False, db=db
        )
        is True
    )


def test_user_group_case_insensitive_match(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "GROUP-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"groups": ["group-a"]}, nuid="jdoe", islog=False, db=db
        )
        is True
    )


def test_user_group_missing_claim_treated_as_no_membership(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert oauth_auth.user_group({}, nuid="jdoe", islog=False, db=db) is False


def test_user_group_unexpected_claim_type_is_safe(monkeypatch):
    """A non-list, non-string groups claim (e.g. dict) is treated as empty."""

    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "groups")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"groups": {"unexpected": True}},
            nuid="jdoe",
            islog=False,
            db=db,
        )
        is False
    )


def test_user_group_honors_custom_claim_name(monkeypatch):
    """`OIDC_GROUPS_CLAIM` reroutes the lookup to a different claim."""

    monkeypatch.setattr(settings, "OIDC_ALLOWED_GROUPS", "Group-A")
    monkeypatch.setattr(settings, "OIDC_GROUPS_CLAIM", "roles")
    db = _mock_db()
    assert (
        oauth_auth.user_group(
            {"roles": ["Group-A"], "groups": []},
            nuid="jdoe",
            islog=False,
            db=db,
        )
        is True
    )


# --------------------------------------------------------------------------- #
# get_end_session_endpoint                                                    #
# --------------------------------------------------------------------------- #


def test_end_session_endpoint_none_when_no_issuer(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ISSUER", None)
    assert oauth_auth.get_end_session_endpoint() is None


def test_end_session_endpoint_returns_from_discovery(monkeypatch):
    monkeypatch.setattr(
        settings, "OIDC_ISSUER", "https://idp.example.com/tenant"
    )
    fake_response = Mock()
    fake_response.json.return_value = {
        "end_session_endpoint": "https://idp.example.com/tenant/logout"
    }
    fake_response.raise_for_status.return_value = None
    monkeypatch.setattr(requests, "get", Mock(return_value=fake_response))
    assert (
        oauth_auth.get_end_session_endpoint()
        == "https://idp.example.com/tenant/logout"
    )


def test_end_session_endpoint_none_on_discovery_failure(monkeypatch):
    monkeypatch.setattr(
        settings, "OIDC_ISSUER", "https://idp.example.com/tenant"
    )
    monkeypatch.setattr(
        requests,
        "get",
        Mock(side_effect=requests.ConnectionError("nope")),
    )
    assert oauth_auth.get_end_session_endpoint() is None


def test_end_session_endpoint_none_when_discovery_missing_field(
    monkeypatch,
):
    """
    Discovery doc without `end_session_endpoint` -> None (SLO not supported).
    """

    monkeypatch.setattr(
        settings, "OIDC_ISSUER", "https://idp.example.com/tenant"
    )
    fake_response = Mock()
    fake_response.json.return_value = {"issuer": "x"}
    fake_response.raise_for_status.return_value = None
    monkeypatch.setattr(requests, "get", Mock(return_value=fake_response))
    assert oauth_auth.get_end_session_endpoint() is None
