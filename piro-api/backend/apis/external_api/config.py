from pathlib import Path

from pydantic import BaseSettings, Field


class ExternalAPISettings(BaseSettings):
    """Read bounded integration settings independently of human
    authentication."""

    enabled: bool = False
    max_cases: int = Field(default=100, ge=1, le=500)
    max_records: int = Field(default=5000, ge=1, le=50000)
    daily_records: int = Field(default=50000, ge=1)
    requests_per_minute: int = Field(default=30, ge=1)
    max_concurrent: int = Field(default=2, ge=1, le=20)
    query_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_body_bytes: int = Field(default=65536, ge=1024, le=1048576)

    class Config:
        """Configure environment loading."""

        env_prefix: str = "EXTERNAL_API_"
        env_file: str = str(Path(__file__).resolve().parents[2] / ".env")
        extra: str = "ignore"
