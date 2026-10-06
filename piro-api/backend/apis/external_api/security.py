import hashlib
import hmac
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.engine import Connection, RowMapping

from .errors import ExternalAPIError
from .models import clients, keys
from .timeutil import database_now, restore_instant

SCOPE: str = "linked-orders:read"
KEY_PATTERN: re.Pattern[str] = re.compile(
    r"piro_([0-9a-f]{32})_([A-Za-z0-9_-]{43})"
)


@dataclass(frozen=True)
class Principal:
    """The verified integration identity and authorized scope."""

    client_id: str
    key_id: str
    scope: str


def hash_key(value: str) -> str:
    """Hash a high-entropy credential for storage and verification."""
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def key_id(value: str | None) -> str | None:
    """Extract the public identifier only from a well-formed credential."""
    match: re.Match[str] | None = KEY_PATTERN.fullmatch(value or "")
    return match.group(1) if match else None


def authenticate(connection: Connection, value: str | None) -> Principal:
    """Verify the credential and current client state against the database."""
    identifier: str | None = key_id(value)
    if identifier is None or value is None:
        raise ExternalAPIError(
            401, "invalid_api_key", "A valid X-API-Key is required."
        )
    row: RowMapping | None = (
        connection.execute(
            select(keys, clients.c.IsActive, clients.c.Scope)
            .join(clients, keys.c.ClientId == clients.c.ClientId)
            .where(keys.c.KeyId == identifier)
        )
        .mappings()
        .first()
    )
    if (
        row is None
        or not hmac.compare_digest(row.SecretHash, hash_key(value))
        or row.RevokedAt is not None
        or restore_instant(row.ExpiresAt, row.ExpiresAtOffsetMinutes)
        <= database_now(connection)
    ):
        raise ExternalAPIError(
            401, "invalid_api_key", "A valid X-API-Key is required."
        )
    if not row.IsActive:
        raise ExternalAPIError(
            403, "integration_disabled", "This integration is disabled."
        )
    return Principal(row.ClientId, row.KeyId, row.Scope)
