"""Administrator Command Line Interface (CLI) for the External API.

Run from backend: python -m apis.external_api.admin --help."""

import argparse
import getpass
import json
import secrets
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from db.engine import create_database_engine
from sqlalchemy import insert, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import ExternalAPISettings
from .errors import ExternalAPIError
from .models import audits, clients, keys, usage
from .security import SCOPE, hash_key
from .service import lock_client
from .timeutil import (
    EASTERN,
    database_now,
    eastern_day,
    eastern_naive,
    eastern_offset,
)


def admin_audit(
    connection: Connection,
    event: str,
    actor: str,
    client_id: str,
    key_identifier: str | None = None,
) -> None:
    """Log an administrator action.

    This logging happens in the same transaction as the change that triggered
    it."""
    connection.execute(
        insert(audits).values(
            RequestId=uuid4().hex,
            ClientId=client_id,
            KeyId=key_identifier,
            Event=event,
            OccurredAt=eastern_naive(database_now(connection)),
            Actor=actor,
            RecordCount=0,
            StatusCode=200,
            ElapsedMs=0,
        )
    )


def validate_label(value: str, label: str) -> str:
    """Validate labels (string names) used for administrator actions."""
    value = value.strip()

    if not value or len(value) > 100 or any(ord(char) < 32 for char in value):
        raise ValueError(f"{label} must contain 1-100 printable characters.")

    return value


def create_client(engine: Engine, name: str, actor: str) -> str:
    """Create an integration identity and initialize its shared usage
    counters."""
    name, actor = validate_label(name, "Name"), validate_label(actor, "Actor")

    identifier: str = uuid4().hex

    with engine.begin() as connection:
        now: datetime = database_now(connection)
        connection.execute(
            insert(clients).values(
                ClientId=identifier,
                Name=name,
                IsActive=True,
                Scope=SCOPE,
                CreatedAt=eastern_naive(now),
                CreatedBy=actor,
            )
        )

        connection.execute(
            insert(usage).values(
                ClientId=identifier,
                QuotaDay=eastern_day(now),
                ReturnedRecords=0,
                Minute=eastern_naive(now).replace(second=0, microsecond=0),
                MinuteOffsetMinutes=eastern_offset(now),
                RequestCount=0,
            )
        )

        admin_audit(connection, "client_created", actor, identifier)

    return identifier


def issue_key(
    engine: Engine, client_id: str, actor: str, expires_days: int = 90
) -> dict[str, str]:
    """Issue a random credential, storing only its verifier and expiry."""
    actor = validate_label(actor, "Actor")
    if not 1 <= expires_days <= 3660:
        raise ValueError("expires-days must be between 1 and 3660.")

    identifier: str = uuid4().hex
    token: str = f"piro_{identifier}_{secrets.token_urlsafe(32)}"

    with engine.begin() as connection:
        lock_client(connection, client_id)
        if not connection.scalar(
            select(clients.c.IsActive).where(clients.c.ClientId == client_id)
        ):
            raise ValueError("Enable the integration before issuing a key.")
        now: datetime = database_now(connection)
        expiry: datetime = now + timedelta(days=expires_days)
        connection.execute(
            insert(keys).values(
                KeyId=identifier,
                ClientId=client_id,
                SecretHash=hash_key(token),
                CreatedAt=eastern_naive(now),
                ExpiresAt=eastern_naive(expiry),
                ExpiresAtOffsetMinutes=eastern_offset(expiry),
                CreatedBy=actor,
            )
        )
        admin_audit(connection, "key_created", actor, client_id, identifier)

    return {
        "key_id": identifier,
        "api_key": token,
        "expires_at": expiry.astimezone(EASTERN).isoformat(),
    }


def set_client_active(
    engine: Engine, client_id: str, actor: str, active: bool
) -> None:
    """Enable or disable admissions for an integration and audit the change."""
    actor = validate_label(actor, "Actor")
    with engine.begin() as connection:
        lock_client(connection, client_id)
        connection.execute(
            update(clients)
            .where(clients.c.ClientId == client_id)
            .values(IsActive=active)
        )
        admin_audit(
            connection,
            "client_enabled" if active else "client_disabled",
            actor,
            client_id,
        )


def revoke_key(engine: Engine, identifier: str, actor: str) -> None:
    """Revoke a key while retaining its identity for audit history."""
    actor = validate_label(actor, "Actor")
    with engine.begin() as connection:
        client_id = connection.scalar(
            select(keys.c.ClientId).where(keys.c.KeyId == identifier)
        )
        if client_id is None:
            raise ValueError("Unknown key ID.")
        lock_client(connection, client_id)
        connection.execute(
            update(keys)
            .where(
                keys.c.KeyId == identifier,
                keys.c.RevokedAt.is_(None),
            )
            .values(RevokedAt=eastern_naive(database_now(connection)))
        )
        admin_audit(connection, "key_revoked", actor, client_id, identifier)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the requested administrator command without logging secrets."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=__doc__
    )
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-client")
    create.add_argument("--name", required=True)
    issue = commands.add_parser(
        "issue-key",
        help="Print a new secret once; existing keys remain valid for rotation.",  # noqa:E501
    )
    issue.add_argument("--client-id", required=True)
    issue.add_argument("--expires-days", type=int, default=90)
    revoke = commands.add_parser("revoke-key")
    revoke.add_argument("--key-id", required=True)
    enable = commands.add_parser("enable-client")
    disable = commands.add_parser("disable-client")
    for command in (enable, disable):
        command.add_argument("--client-id", required=True)
    commands.add_parser("list-clients")
    listing = commands.add_parser("list-keys")
    listing.add_argument("--client-id", required=True)
    for command in (create, issue, revoke, enable, disable):
        command.add_argument("--actor", default=getpass.getuser())
    args: argparse.Namespace = parser.parse_args(argv)
    engine: Engine = create_database_engine(
        query_timeout_seconds=ExternalAPISettings().query_timeout_seconds
    )

    try:
        if args.command == "create-client":
            result: dict[str, Any] | list[dict[str, Any]] = {
                "client_id": create_client(engine, args.name, args.actor)
            }

        elif args.command == "issue-key":
            result = issue_key(
                engine, args.client_id, args.actor, args.expires_days
            )

        elif args.command == "revoke-key":
            revoke_key(engine, args.key_id, args.actor)
            result = {"revoked": args.key_id}

        elif args.command in {"enable-client", "disable-client"}:
            active = args.command == "enable-client"
            set_client_active(engine, args.client_id, args.actor, active)
            result = {"client_id": args.client_id, "active": active}

        else:
            with engine.connect() as connection:

                query = (
                    select(
                        clients.c.ClientId,
                        clients.c.Name,
                        clients.c.IsActive,
                        clients.c.Scope,
                    )
                    if args.command == "list-clients"
                    else select(
                        keys.c.KeyId,
                        keys.c.ClientId,
                        keys.c.CreatedAt,
                        keys.c.ExpiresAt,
                        keys.c.ExpiresAtOffsetMinutes,
                        keys.c.RevokedAt,
                    ).where(keys.c.ClientId == args.client_id)
                )

                result = [
                    dict(row) for row in connection.execute(query).mappings()
                ]

        print(json.dumps(result, default=str, indent=2))
        return 0

    except (ValueError, SQLAlchemyError, ExternalAPIError) as exc:
        # Avoid printing database parameters, credentials, or SQL statements.
        parser.exit(
            1,
            f"Command failed ({type(exc).__name__}). Check the identifiers, schema deployment, and database access.\n",  # noqa:E501
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
