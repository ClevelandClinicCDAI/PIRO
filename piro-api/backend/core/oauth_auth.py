"""OIDC / OAuth 2.0 identity provider integration.

This module mirrors the responsibility surface of :mod:`core.ldap_auth`
so that :func:`core.security_user.authenticate_user` can dispatch to
either provider based on ``settings.AUTH_MODE``.

Only consulted when ``AUTH_MODE == "OAUTH"``. Nothing here runs when the
API is configured for LDAP.
"""

from __future__ import annotations

from threading import Lock
from typing import Any
from urllib.parse import urljoin

import jwt
import requests
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from core.config import settings
from core.constants import Constants
from db.repository.user import create_user_log
from logger import logger

SUCCESS: str = Constants.StatusCode.S.name
ERROR: str = Constants.StatusCode.E.name

OAUTH: str = Constants.LoginTypeCode.OAUTH.name
ADGROUP: str = Constants.LoginTypeCode.ADGROUP.name
CREDENTIAL: str = Constants.LoginTypeCode.CREDENTIAL.name

# Module-level cache for the JWKS client. PyJWKClient handles its own
# key caching + rotation internally; we only need to construct it once
# per process. Guarded by a lock so concurrent first-time requests don't
# race on discovery.
_jwks_client: PyJWKClient | None = None
_jwks_client_lock: Lock = Lock()
_discovery_document: dict[str, Any] | None = None


def _discover(issuer: str) -> dict[str, Any]:
    """Fetch and cache the OIDC discovery document for the issuer."""

    global _discovery_document
    if _discovery_document is not None:
        return _discovery_document

    discovery_url = urljoin(
        issuer.rstrip("/") + "/", ".well-known/openid-configuration"
    )
    response = requests.get(discovery_url, timeout=10)
    response.raise_for_status()
    _discovery_document = response.json()
    return _discovery_document


def _get_jwks_client() -> PyJWKClient:
    """Return a cached ``PyJWKClient`` for the configured issuer.

    Resolves ``OIDC_JWKS_URL`` from config first, falling back to the
    ``jwks_uri`` field of the issuer's discovery document.
    """

    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client

    with _jwks_client_lock:
        if _jwks_client is not None:  # double-check under lock
            return _jwks_client

        if not settings.OIDC_ISSUER:
            raise RuntimeError(
                "OIDC_ISSUER is not configured; cannot verify OAuth tokens."
            )

        jwks_url = settings.OIDC_JWKS_URL
        if not jwks_url:
            discovery = _discover(settings.OIDC_ISSUER)
            jwks_url = discovery.get("jwks_uri")
            if not jwks_url:
                raise RuntimeError(
                    "Issuer discovery document did not include a jwks_uri."
                )

        _jwks_client = PyJWKClient(jwks_url)
        return _jwks_client


def get_end_session_endpoint() -> str | None:
    """Return the IdP's RP-initiated logout URL, or ``None`` if absent."""

    if not settings.OIDC_ISSUER:
        return None
    try:
        discovery = _discover(settings.OIDC_ISSUER)
    except requests.RequestException as exc:
        logger.warning(
            f"Failed to fetch OIDC discovery document for logout: {exc}"
        )
        return None
    return discovery.get("end_session_endpoint")


def verify_oauth_token(
    id_token: str, islog: bool, db: Session
) -> dict[str, Any] | None:
    """Validate an OIDC id_token and return its claims.

    Returns the decoded claims dict on success, or ``None`` on any
    verification failure. Failures are logged to ``UserLog`` with
    ``LoginTypeCode.OAUTH`` so the audit trail records why a login was
    rejected without disclosing details to the caller.
    """

    if not settings.OIDC_ISSUER:
        message = (
            "OIDC_ISSUER not configured; refusing to validate OAuth token."
        )
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None

    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    except Exception as exc:
        message = f"Unable to resolve JWKS signing key: {exc}"
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None

    algorithms = [
        alg.strip()
        for alg in settings.OIDC_ALGORITHMS.split(",")
        if alg.strip()
    ]
    decode_kwargs: dict[str, Any] = {
        "issuer": settings.OIDC_ISSUER,
        "leeway": settings.OIDC_CLOCK_SKEW_SECONDS,
        "algorithms": algorithms,
    }
    if settings.OIDC_AUDIENCE:
        decode_kwargs["audience"] = settings.OIDC_AUDIENCE
    else:
        # Skip audience verification when no audience is configured;
        # mock IdPs and some enterprise setups don't populate `aud`.
        decode_kwargs["options"] = {"verify_aud": False}

    try:
        claims = jwt.decode(id_token, signing_key.key, **decode_kwargs)
    except jwt.ExpiredSignatureError:
        message = "OAuth id_token rejected: expired."
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None
    except jwt.InvalidIssuerError:
        message = (
            f"OAuth id_token rejected: issuer does not match "
            f"'{settings.OIDC_ISSUER}'."
        )
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None
    except jwt.InvalidAudienceError:
        message = (
            f"OAuth id_token rejected: audience does not match "
            f"'{settings.OIDC_AUDIENCE}'."
        )
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None
    except jwt.InvalidTokenError as exc:
        message = f"OAuth id_token rejected: {exc}"
        logger.error(message)
        create_user_log("", -1, -1, ERROR, OAUTH, message, islog, db=db)
        return None

    nuid = claims.get(settings.OIDC_NUID_CLAIM, "")
    message = (
        f"OAuth id_token verified for '{nuid}' via issuer "
        f"'{settings.OIDC_ISSUER}'."
    )
    logger.info(message)
    create_user_log(nuid, -1, -1, SUCCESS, OAUTH, message, islog, db=db)
    return claims


def extract_identity(claims: dict[str, Any]) -> dict[str, str]:
    """Map token claims to the fields required by the PIRO user table.

    Applies the fallback chain documented in the migration plan:

    * ``firstName`` <- given-name claim -> parsed ``name`` -> ``""``
    * ``lastName``  <- family-name claim -> parsed ``name`` -> ``""``
    * ``nuid``      <- configured NUID claim -> ``""``

    Empty-string fallbacks (rather than ``None``) satisfy the NOT NULL
    constraints on the ``NUID``, ``FirstName``, and ``LastName`` columns
    in :class:`db.models.User.User`.
    """

    nuid = normalize_nuid(claims.get(settings.OIDC_NUID_CLAIM))
    first_name = str(claims.get(settings.OIDC_GIVEN_NAME_CLAIM) or "")
    last_name = str(claims.get(settings.OIDC_FAMILY_NAME_CLAIM) or "")

    if (not first_name or not last_name) and claims.get("name"):
        # Fallback: split the display-name claim on the first whitespace.
        parts = str(claims["name"]).strip().split(None, 1)
        if parts:
            if not first_name:
                first_name = parts[0]
            if not last_name and len(parts) > 1:
                last_name = parts[1]

    return {
        "nuid": nuid,
        "firstName": first_name,
        "lastName": last_name,
    }


def normalize_nuid(raw_nuid: Any) -> str:
    """Normalize Entra-style usernames to PIRO's stored NUID format.

    PIRO stores NUIDs as lowercase local parts (for example,
    ``CUMBOJ@ccf.org`` -> ``cumboj``). Values that do not look like email
    addresses are preserved after trimming and lowercasing.
    """

    nuid = str(raw_nuid or "").strip().lower()
    if "@" in nuid:
        nuid = nuid.split("@", 1)[0]
    return nuid


def user_group(
    claims: dict[str, Any],
    nuid: str,
    islog: bool,
    db: Session,
) -> bool:
    """Return True if the token's group claim intersects OIDC_ALLOWED_GROUPS.

    OR semantics: membership in any single configured group grants access.
    Empty ``OIDC_ALLOWED_GROUPS`` means the check is disabled (any
    authenticated user passes) — matching the behaviour of an unconfigured
    ``AD_SECURITY_GROUP`` in the LDAP path.
    """

    allowed = [
        group.strip()
        for group in settings.OIDC_ALLOWED_GROUPS.split(",")
        if group.strip()
    ]
    if not allowed:
        return True

    token_groups_raw = claims.get(settings.OIDC_GROUPS_CLAIM, [])
    if isinstance(token_groups_raw, str):
        # Some IdPs emit a single group as a scalar rather than a list.
        token_groups = [token_groups_raw]
    elif isinstance(token_groups_raw, list):
        token_groups = [str(group) for group in token_groups_raw]
    else:
        token_groups = []

    allowed_set = {group.lower() for group in allowed}
    is_member = any(group.lower() in allowed_set for group in token_groups)

    if is_member:
        message = (
            f"User '{nuid}' authorized via OAuth group claim "
            f"(matched one of: {allowed})."
        )
        logger.info(message)
        create_user_log(nuid, -1, -1, SUCCESS, ADGROUP, message, islog, db=db)
    else:
        message = (
            f"User '{nuid}' NOT authorized: OAuth `groups` claim "
            f"{token_groups} does not intersect allowed groups {allowed}."
        )
        logger.error(message)
        create_user_log(nuid, -1, -1, ERROR, ADGROUP, message, islog, db=db)

    return is_member
