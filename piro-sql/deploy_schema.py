#!/usr/bin/env python3
"""
Deploy PIRO SQL schema objects to a non-Docker SQL Server instance.
"""

from __future__ import annotations

import argparse
import heapq
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


CREATE_PATTERN = re.compile(r"CREATE\s+TABLE\s+\[?(?:dbo\.)?([^\]\s]+)\]?", re.IGNORECASE)
REFERENCES_PATTERN = re.compile(r"REFERENCES\s+\[?(?:dbo\.)?([^\]\s]+)\]?", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy PIRO SQL schema objects using sqlcmd."
    )
    parser.add_argument("--server", required=True, help="SQL Server host name or IP.")
    parser.add_argument("--port", type=int, default=1433, help="SQL Server port (default: 1433).")
    parser.add_argument("--user", required=True, help="SQL login (example: sa).")
    parser.add_argument("--password", required=True, help="SQL login password.")
    parser.add_argument("--database", default="PIRO", help="Target database name (default: PIRO).")
    parser.add_argument(
        "--scripts-root",
        default=str(Path(__file__).resolve().parent),
        help="Root folder that contains Table/View/PLSQL/etc. (default: piro-sql folder).",
    )
    parser.add_argument(
        "--sqlcmd-path",
        default=None,
        help="Path to sqlcmd binary. If omitted, script auto-detects common locations.",
    )
    parser.add_argument(
        "--force-reset",
        action="store_true",
        help="Drop and recreate the target database before deployment.",
    )
    parser.add_argument(
        "--include-ssis",
        action="store_true",
        help="Also deploy SSIS/TABLES, SSIS/PROCS, and SSIS/JOBS scripts.",
    )
    parser.add_argument(
        "--max-passes",
        type=int,
        default=10,
        help="Maximum retry passes per directory for dependency failures (default: 10).",
    )
    parser.add_argument(
        "--trust-server-certificate",
        action="store_true",
        help="Pass -C to sqlcmd (useful with self-signed TLS certs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would run without executing sqlcmd.",
    )
    return parser.parse_args()


def log(message: str) -> None:
    print(message, flush=True)


def resolve_sqlcmd(explicit_path: str | None) -> str:
    if explicit_path:
        candidate = Path(explicit_path)
        if not candidate.exists():
            raise FileNotFoundError(f"sqlcmd not found at --sqlcmd-path: {explicit_path}")
        return str(candidate)

    path_hit = shutil.which("sqlcmd")
    if path_hit:
        return path_hit

    common_paths = [
        "/opt/mssql-tools18/bin/sqlcmd",
        "/opt/mssql-tools/bin/sqlcmd",
        "/usr/local/bin/sqlcmd",
    ]
    for candidate in common_paths:
        if Path(candidate).exists():
            return candidate

    raise FileNotFoundError(
        "sqlcmd binary not found. Install sqlcmd or pass --sqlcmd-path."
    )


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
    dry_run: bool = False,
) -> int:
    cmd = list(base_cmd)
    if query is not None:
        cmd.extend(["-Q", query])
    if input_file is not None:
        cmd.extend(["-i", str(input_file)])

    if dry_run:
        log(f"DRY RUN: {' '.join(cmd)}")
        return 0

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        if proc.stdout.strip():
            log(proc.stdout.rstrip())
        if proc.stderr.strip():
            log(proc.stderr.rstrip())
    return proc.returncode


def read_sql_text(path: Path) -> str:
    for encoding in ("utf-16-le", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def ordered_table_scripts(table_dir: Path) -> list[Path]:
    files = sorted(table_dir.glob("*.sql"))
    texts = {path: read_sql_text(path) for path in files}

    table_to_file: dict[str, Path] = {}
    for path in files:
        match = CREATE_PATTERN.search(texts[path])
        if match:
            table_to_file[match.group(1).strip().lower()] = path

    deps: dict[str, set[str]] = defaultdict(set)
    for table, path in table_to_file.items():
        for ref in REFERENCES_PATTERN.findall(texts[path]):
            ref_name = ref.strip().lower()
            if ref_name != table and ref_name in table_to_file:
                deps[table].add(ref_name)
        deps.setdefault(table, set())

    indegree = {table: 0 for table in table_to_file}
    dependents: dict[str, set[str]] = defaultdict(set)
    for table, references in deps.items():
        for ref in references:
            indegree[table] += 1
            dependents[ref].add(table)

    heap = [table for table, degree in indegree.items() if degree == 0]
    heapq.heapify(heap)

    ordered: list[Path] = []
    processed: set[str] = set()
    while heap:
        table = heapq.heappop(heap)
        ordered.append(table_to_file[table])
        processed.add(table)
        for dependent in dependents.get(table, set()):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(heap, dependent)

    remaining = sorted(table_to_file[t] for t in (set(table_to_file) - processed))
    ordered.extend(remaining)

    ordered_set = set(ordered)
    for path in files:
        if path not in ordered_set:
            ordered.append(path)
    return ordered


def collect_scripts(path: Path, is_table_dir: bool) -> list[Path]:
    if not path.exists():
        return []
    if is_table_dir:
        return ordered_table_scripts(path)
    return sorted(path.rglob("*.sql"))


def apply_dir(
    path: Path,
    *,
    is_table_dir: bool,
    base_cmd: list[str],
    dry_run: bool,
    max_passes: int,
) -> None:
    files = collect_scripts(path, is_table_dir)
    if not files:
        return

    pending = list(files)
    pass_num = 1
    while pending:
        log(f"Applying directory: {path} (pass {pass_num})")
        deferred: list[Path] = []
        for file_path in pending:
            log(f"Applying {file_path}")
            rc = run_sql(base_cmd, input_file=file_path, dry_run=dry_run)
            if rc != 0:
                deferred.append(file_path)
                log(f"Deferring {file_path} until next pass")

        if deferred and len(deferred) == len(pending):
            raise RuntimeError(f"All scripts failed in {path}; cannot make progress.")

        pending = deferred
        pass_num += 1
        if pending and pass_num > max_passes:
            raise RuntimeError(f"Exceeded max passes ({max_passes}) in {path}.")


def main() -> int:
    args = parse_args()

    scripts_root = Path(args.scripts_root).resolve()
    if not scripts_root.exists():
        raise FileNotFoundError(f"Scripts root does not exist: {scripts_root}")

    sqlcmd = resolve_sqlcmd(args.sqlcmd_path)
    log(f"Using sqlcmd: {sqlcmd}")
    log(f"Scripts root: {scripts_root}")

    master_cmd = build_base_cmd(
        sqlcmd=sqlcmd,
        server=args.server,
        port=args.port,
        user=args.user,
        password=args.password,
        database="master",
        trust_server_certificate=args.trust_server_certificate,
    )
    target_cmd = build_base_cmd(
        sqlcmd=sqlcmd,
        server=args.server,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        trust_server_certificate=args.trust_server_certificate,
    )

    if run_sql(master_cmd, query="SELECT 1", dry_run=args.dry_run) != 0:
        raise RuntimeError("Failed to connect to SQL Server with supplied credentials.")

    if args.force_reset:
        log(f"Resetting database [{args.database}]")
        drop_query = (
            f"IF DB_ID('{args.database}') IS NOT NULL "
            f"BEGIN ALTER DATABASE [{args.database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
            f"DROP DATABASE [{args.database}]; END"
        )
        if run_sql(master_cmd, query=drop_query, dry_run=args.dry_run) != 0:
            raise RuntimeError("Failed to drop existing database.")

    log(f"Ensuring database [{args.database}] exists")
    create_query = f"IF DB_ID('{args.database}') IS NULL CREATE DATABASE [{args.database}]"
    if run_sql(master_cmd, query=create_query, dry_run=args.dry_run) != 0:
        raise RuntimeError("Failed to create database.")

    deploy_dirs: list[tuple[str, bool]] = [
        ("Table", True),
        ("Function", False),
        ("View/PIRO", False),
        ("View/SOLR", False),
        ("PLSQL", False),
        ("Airflow", False),
    ]
    if args.include_ssis:
        deploy_dirs.extend(
            [
                ("SSIS/TABLES", False),
                ("SSIS/PROCS", False),
                ("SSIS/JOBS", False),
            ]
        )

    for rel_dir, is_table_dir in deploy_dirs:
        apply_dir(
            scripts_root / rel_dir,
            is_table_dir=is_table_dir,
            base_cmd=target_cmd,
            dry_run=args.dry_run,
            max_passes=args.max_passes,
        )

    log("Deployment completed successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
