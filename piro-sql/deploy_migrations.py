#!/usr/bin/env python3
"""
Apply incremental SQL migrations to an existing SQL Server database.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply pending migrations from piro-sql/Migrations using sqlcmd."
    )
    parser.add_argument("--server", required=True, help="SQL Server host name or IP.")
    parser.add_argument("--port", type=int, default=1433, help="SQL Server port (default: 1433).")
    parser.add_argument("--user", required=True, help="SQL login (example: sa).")
    parser.add_argument("--password", required=True, help="SQL login password.")
    parser.add_argument("--database", required=True, help="Existing target database name (example: PIRO).")
    parser.add_argument(
        "--migrations-dir",
        default=str(Path(__file__).resolve().parent / "Migrations"),
        help="Folder containing versioned .sql migration files (default: piro-sql/Migrations).",
    )
    parser.add_argument(
        "--sqlcmd-path",
        default=None,
        help="Path to sqlcmd binary. If omitted, script auto-detects common locations.",
    )
    parser.add_argument(
        "--table-name",
        default="dbo.SchemaMigrations",
        help="Tracking table in schema.table format (default: dbo.SchemaMigrations).",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Mark all currently pending migration files as applied without executing them.",
    )
    parser.add_argument(
        "--allow-checksum-mismatch",
        action="store_true",
        help="Do not fail if an already-applied script has changed content (not recommended).",
    )
    parser.add_argument(
        "--trust-server-certificate",
        action="store_true",
        help="Pass -C to sqlcmd (useful with self-signed TLS certs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions only; do not execute migrations or writes.",
    )
    return parser.parse_args()


def log(message: str) -> None:
    print(message, flush=True)


def fail(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def split_schema_table(value: str) -> tuple[str, str]:
    parts = value.split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        fail("--table-name must be in schema.table format, example: dbo.SchemaMigrations")
    return parts[0], parts[1]


def resolve_sqlcmd(explicit_path: str | None) -> str:
    if explicit_path:
        candidate = Path(explicit_path)
        if not candidate.exists():
            fail(f"sqlcmd not found at --sqlcmd-path: {explicit_path}")
        return str(candidate)

    path_hit = shutil.which("sqlcmd")
    if path_hit:
        return path_hit

    for candidate in (
        "/opt/mssql-tools18/bin/sqlcmd",
        "/opt/mssql-tools/bin/sqlcmd",
        "/usr/local/bin/sqlcmd",
    ):
        if Path(candidate).exists():
            return candidate

    fail("sqlcmd binary not found. Install sqlcmd or pass --sqlcmd-path.")


def sql_literal(value: str) -> str:
    return value.replace("'", "''")


def build_base_cmd(
    sqlcmd: str,
    server: str,
    port: int,
    user: str,
    password: str,
    database: str,
    trust_server_certificate: bool,
) -> list[str]:
    cmd = [
        sqlcmd,
        "-S",
        f"{server},{port}",
        "-U",
        user,
        "-P",
        password,
        "-d",
        database,
        "-b",
    ]
    if trust_server_certificate:
        cmd.append("-C")
    return cmd


def run_sql(
    base_cmd: list[str],
    *,
    query: str | None = None,
    input_file: Path | None = None,
    extra_args: list[str] | None = None,
    dry_run: bool = False,
) -> tuple[int, str, str]:
    cmd = list(base_cmd)
    if extra_args:
        cmd.extend(extra_args)
    if query is not None:
        cmd.extend(["-Q", query])
    if input_file is not None:
        cmd.extend(["-i", str(input_file)])

    if dry_run:
        log(f"DRY RUN: {' '.join(cmd)}")
        return 0, "", ""

    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def parse_applied_rows(output: str) -> dict[str, str]:
    applied: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or "|" not in line or line.startswith("("):
            continue
        name, checksum = line.split("|", 1)
        name = name.strip()
        checksum = checksum.strip().lower()
        if name:
            applied[name] = checksum
    return applied


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_tracking_table(
    base_cmd: list[str],
    *,
    schema: str,
    table: str,
    dry_run: bool,
) -> None:
    query = f"""
SET NOCOUNT ON;
IF OBJECT_ID(N'[{schema}].[{table}]', N'U') IS NULL
BEGIN
    EXEC('CREATE TABLE [{schema}].[{table}](
        [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ScriptName] NVARCHAR(512) NOT NULL UNIQUE,
        [ChecksumSha256] CHAR(64) NOT NULL,
        [AppliedUtc] DATETIME2(3) NOT NULL CONSTRAINT [DF_{table}_AppliedUtc] DEFAULT SYSUTCDATETIME()
    )');
END;
"""
    code, stdout, stderr = run_sql(base_cmd, query=query, dry_run=dry_run)
    if code != 0:
        fail(f"Failed to ensure tracking table [{schema}].[{table}]\n{stdout}\n{stderr}")


def get_applied_migrations(
    base_cmd: list[str],
    *,
    schema: str,
    table: str,
    dry_run: bool,
) -> dict[str, str]:
    query = f"""
SET NOCOUNT ON;
SELECT [ScriptName] + '|' + [ChecksumSha256]
FROM [{schema}].[{table}]
ORDER BY [ScriptName];
"""
    code, stdout, stderr = run_sql(
        base_cmd,
        query=query,
        extra_args=["-h", "-1", "-W"],
        dry_run=dry_run,
    )
    if code != 0:
        fail(f"Failed reading applied migrations\n{stdout}\n{stderr}")
    if dry_run:
        return {}
    return parse_applied_rows(stdout)


def insert_applied_migration(
    base_cmd: list[str],
    *,
    schema: str,
    table: str,
    script_name: str,
    checksum: str,
    dry_run: bool,
) -> None:
    name_sql = sql_literal(script_name)
    checksum_sql = sql_literal(checksum)
    query = f"""
SET NOCOUNT ON;
INSERT INTO [{schema}].[{table}] ([ScriptName], [ChecksumSha256])
VALUES (N'{name_sql}', '{checksum_sql}');
"""
    code, stdout, stderr = run_sql(base_cmd, query=query, dry_run=dry_run)
    if code != 0:
        fail(f"Failed to record migration {script_name}\n{stdout}\n{stderr}")


def migration_files(migrations_dir: Path) -> list[Path]:
    if not migrations_dir.exists():
        fail(f"Migrations directory not found: {migrations_dir}")
    return sorted(path for path in migrations_dir.rglob("*.sql") if path.is_file())


def main() -> int:
    args = parse_args()
    schema, table = split_schema_table(args.table_name)
    migrations_dir = Path(args.migrations_dir).resolve()
    files = migration_files(migrations_dir)
    sqlcmd = resolve_sqlcmd(args.sqlcmd_path)

    log(f"Using sqlcmd: {sqlcmd}")
    log(f"Migrations directory: {migrations_dir}")
    log(f"Tracking table: [{schema}].[{table}]")

    if not files:
        log("No .sql migration files found. Nothing to do.")
        return 0

    base_cmd = build_base_cmd(
        sqlcmd=sqlcmd,
        server=args.server,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        trust_server_certificate=args.trust_server_certificate,
    )

    code, _, stderr = run_sql(base_cmd, query="SELECT 1", dry_run=args.dry_run)
    if code != 0:
        fail(f"Failed to connect to target database [{args.database}]\n{stderr}")

    ensure_tracking_table(base_cmd, schema=schema, table=table, dry_run=args.dry_run)
    applied = get_applied_migrations(base_cmd, schema=schema, table=table, dry_run=args.dry_run)

    pending: list[tuple[Path, str, str]] = []
    skipped = 0
    for file_path in files:
        script_name = file_path.relative_to(migrations_dir).as_posix()
        checksum = sha256_file(file_path)
        existing_checksum = applied.get(script_name)
        if existing_checksum is not None:
            if existing_checksum != checksum.lower() and not args.allow_checksum_mismatch:
                fail(
                    "Checksum mismatch for already-applied migration "
                    f"{script_name}. Create a new migration file instead of editing old ones."
                )
            skipped += 1
            continue
        pending.append((file_path, script_name, checksum))

    if not pending:
        log("No pending migrations. Database is up to date.")
        return 0

    log(f"Pending migrations: {len(pending)}")
    for _, script_name, _ in pending:
        mode_label = "baseline-only" if args.baseline else "apply"
        log(f" - {mode_label}: {script_name}")

    applied_now = 0
    for file_path, script_name, checksum in pending:
        if args.baseline:
            log(f"Recording baseline migration: {script_name}")
            insert_applied_migration(
                base_cmd,
                schema=schema,
                table=table,
                script_name=script_name,
                checksum=checksum,
                dry_run=args.dry_run,
            )
            applied_now += 1
            continue

        log(f"Executing migration: {script_name}")
        code, stdout, stderr = run_sql(base_cmd, input_file=file_path, dry_run=args.dry_run)
        if code != 0:
            fail(f"Migration failed: {script_name}\n{stdout}\n{stderr}")

        insert_applied_migration(
            base_cmd,
            schema=schema,
            table=table,
            script_name=script_name,
            checksum=checksum,
            dry_run=args.dry_run,
        )
        applied_now += 1

    log(
        "Migration run completed. "
        f"Already applied: {skipped}. Newly processed: {applied_now}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
