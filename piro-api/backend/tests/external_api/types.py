"""Typed fixtures shared by the external API regression tests."""

from typing import TypedDict

from apis.external_api.config import ExternalAPISettings
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine


class ApiFixture(TypedDict):
    """A real HTTP client and isolated PostgreSQL integration state."""

    engine: Engine
    config: ExternalAPISettings
    client_id: str
    credential: dict[str, str]
    app: FastAPI
    client: TestClient
    headers: dict[str, str]
