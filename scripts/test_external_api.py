"""Run backend external API tests using an existing localhost PostgreSQL.

Set PIRO_EXTERNAL_TEST_POSTGRES_URL or POSTGRES_* in the environment.
Tests create/drop uniquely named schemas, never the database or existing tables.
Optional SQL Server dialect checks require their separate opt-in variables.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run the selected backend suite with test-only application settings."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "--full-suite",
        action="store_true",
        help="Also run the existing PIRO backend tests.",
    )
    args: argparse.Namespace = parser.parse_args()
    root: Path = Path(__file__).resolve().parents[1]
    test_env: dict[str, str] = dict(
        os.environ,
        DATABASE="SQLITE",
        PROJECT_NAME="PIRO Test",
        PROJECT_VERSION="1.0.0",
        AD_LDAP_PATH="ldap://localhost",
        PYTHONPATH=str(root / "piro-api" / "backend"),
    )
    path: str = (
        "piro-api/backend/tests"
        if args.full_suite
        else "piro-api/backend/tests/external_api"
    )
    return subprocess.run(
        [sys.executable, "-m", "pytest", path, "-q", "--tb=short"],
        cwd=root,
        env=test_env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
