#!/usr/bin/env bash
set -euo pipefail

PIRO_DB_SERVER="${PIRO_DB_SERVER:-}"
PIRO_DB_NAME="${PIRO_DB_NAME:-}"
PIRO_DB_USER="${PIRO_DB_USER:-}"
PIRO_DB_PASSWORD="${PIRO_DB_PASSWORD:-}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

require_env() {
  local name="$1"
  local value="$2"
  [[ -n "$value" ]] || die "Set ${name}"
}

main() {
  require_cmd sqlcmd
  require_env "PIRO_DB_SERVER" "$PIRO_DB_SERVER"
  require_env "PIRO_DB_NAME" "$PIRO_DB_NAME"
  require_env "PIRO_DB_USER" "$PIRO_DB_USER"
  require_env "PIRO_DB_PASSWORD" "$PIRO_DB_PASSWORD"

  local db_name_lc
  db_name_lc="$(echo "$PIRO_DB_NAME" | tr '[:upper:]' '[:lower:]')"
  case "$db_name_lc" in
    master|model|msdb|tempdb)
      die "Refusing to run against system database [$PIRO_DB_NAME]"
      ;;
  esac

  echo "Resetting user objects in [$PIRO_DB_NAME] on [$PIRO_DB_SERVER]..."

  sqlcmd -S "$PIRO_DB_SERVER" -U "$PIRO_DB_USER" -P "$PIRO_DB_PASSWORD" -N -C -b -l 30 -d "$PIRO_DB_NAME" <<'SQL'
SET NOCOUNT ON;

DECLARE @sql nvarchar(max);

-- 1) Drop foreign keys first
SET @sql = N'';
SELECT @sql += N'ALTER TABLE ' + QUOTENAME(s.name) + N'.' + QUOTENAME(t.name)
             + N' DROP CONSTRAINT ' + QUOTENAME(fk.name) + N';' + CHAR(10)
FROM sys.foreign_keys fk
JOIN sys.tables t ON fk.parent_object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA');

IF @sql <> N''
BEGIN
  IF LOWER(@sql) LIKE N'%drop database%'
    THROW 50001, 'Safety check failed: DROP DATABASE is forbidden.', 1;
  EXEC sp_executesql @sql;
END

-- 2) Drop views
SET @sql = N'';
SELECT @sql += N'DROP VIEW ' + QUOTENAME(s.name) + N'.' + QUOTENAME(v.name) + N';' + CHAR(10)
FROM sys.views v
JOIN sys.schemas s ON v.schema_id = s.schema_id
WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA');

IF @sql <> N''
BEGIN
  IF LOWER(@sql) LIKE N'%drop database%'
    THROW 50001, 'Safety check failed: DROP DATABASE is forbidden.', 1;
  EXEC sp_executesql @sql;
END

-- 3) Drop procedures
SET @sql = N'';
SELECT @sql += N'DROP PROCEDURE ' + QUOTENAME(s.name) + N'.' + QUOTENAME(p.name) + N';' + CHAR(10)
FROM sys.procedures p
JOIN sys.schemas s ON p.schema_id = s.schema_id
WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA');

IF @sql <> N''
BEGIN
  IF LOWER(@sql) LIKE N'%drop database%'
    THROW 50001, 'Safety check failed: DROP DATABASE is forbidden.', 1;
  EXEC sp_executesql @sql;
END

-- 4) Drop functions
SET @sql = N'';
SELECT @sql += N'DROP FUNCTION ' + QUOTENAME(s.name) + N'.' + QUOTENAME(o.name) + N';' + CHAR(10)
FROM sys.objects o
JOIN sys.schemas s ON o.schema_id = s.schema_id
WHERE o.type IN ('FN', 'IF', 'TF', 'FS', 'FT')
  AND s.name NOT IN ('sys', 'INFORMATION_SCHEMA');

IF @sql <> N''
BEGIN
  IF LOWER(@sql) LIKE N'%drop database%'
    THROW 50001, 'Safety check failed: DROP DATABASE is forbidden.', 1;
  EXEC sp_executesql @sql;
END

-- 5) Drop tables
SET @sql = N'';
SELECT @sql += N'DROP TABLE ' + QUOTENAME(s.name) + N'.' + QUOTENAME(t.name) + N';' + CHAR(10)
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA');

IF @sql <> N''
BEGIN
  IF LOWER(@sql) LIKE N'%drop database%'
    THROW 50001, 'Safety check failed: DROP DATABASE is forbidden.', 1;
  EXEC sp_executesql @sql;
END
SQL

  echo "Done."
}

main "$@"
