#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SQL_ROOT="${SQL_ROOT:-$ROOT_DIR/piro-sql}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$ROOT_DIR/artifacts/db-migration/$(date +%Y%m%d_%H%M%S)}"

DEV_SERVER="${DEV_SERVER:-}"
DEV_DATABASE="${DEV_DATABASE:-PIRO_DEV}"
SHADOW_DATABASE="${SHADOW_DATABASE:-PIRO_Shadow}"
DEV_USER="${DEV_USER:-}"
DEV_PASS="${DEV_PASS:-}"

INCLUDE_SSIS="${INCLUDE_SSIS:-true}"
INCLUDE_INDEX="${INCLUDE_INDEX:-false}"
MAX_PASSES="${MAX_PASSES:-10}"
APPLY_POST_DATA="${APPLY_POST_DATA:-false}"
SKIP_SHADOW_CREATE="${SKIP_SHADOW_CREATE:-false}"
SOURCE_DACPAC="${SOURCE_DACPAC:-}"

POST_DEPLOY_DATA_SCRIPT="${POST_DEPLOY_DATA_SCRIPT:-$ROOT_DIR/scripts/db/post_deploy_data.sql}"
DEPLOY_REPORT_PATH="${DEPLOY_REPORT_PATH:-$ARTIFACT_DIR/piro_deploy_report.xml}"
MIGRATION_SCRIPT_PATH="${MIGRATION_SCRIPT_PATH:-$ARTIFACT_DIR/piro_migration.sql}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

to_lower() {
  echo "$1" | tr '[:upper:]' '[:lower:]'
}

is_true() {
  case "$(to_lower "$1")" in
    1|true|yes|y) return 0 ;;
    *) return 1 ;;
  esac
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

run_sql() {
  local database="$1"
  shift
  sqlcmd -S "$DEV_SERVER" -U "$DEV_USER" -P "$DEV_PASS" -C -b -d "$database" "$@"
}

apply_file() {
  local file="$1"
  local tmp
  tmp="$(mktemp)"

  local bom
  bom="$(xxd -p -l 2 "$file" | tr -d '\n')"

  case "$bom" in
    fffe) iconv -f UTF-16LE -t UTF-8 "$file" >"$tmp" ;;
    feff) iconv -f UTF-16BE -t UTF-8 "$file" >"$tmp" ;;
    *) cp "$file" "$tmp" ;;
  esac

  # Strip UTF-8 BOM when present; sqlcmd can choke on BOM in piped input.
  awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}1' "$tmp" >"${tmp}.clean"
  mv "${tmp}.clean" "$tmp"

  if [[ "$file" == *"/SSIS/TABLES/"* ]]; then
    local base table_name
    base="$(basename "$file")"
    table_name="${base#*.}"
    table_name="${table_name%%.*}"
    run_sql "$SHADOW_DATABASE" -Q "IF OBJECT_ID('[dbo].[$table_name]', 'U') IS NOT NULL DROP TABLE [dbo].[$table_name];" >/dev/null || true
  fi

  if run_sql "$SHADOW_DATABASE" -i "$tmp"; then
    rm -f "$tmp"
    return 0
  fi

  rm -f "$tmp"
  return 1
}

apply_dir_with_retries() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0

  local pending=()
  local deferred=()
  local file
  local pass=0

  while IFS= read -r file; do
    pending+=("$file")
  done < <(find "$dir" -type f -name '*.sql' | sort)

  [[ ${#pending[@]} -gt 0 ]] || return 0

  while [[ ${#pending[@]} -gt 0 ]]; do
    pass=$((pass + 1))
    deferred=()
    local succeeded=0

    echo "Applying directory: ${dir#$ROOT_DIR/} (pass ${pass})"
    for file in "${pending[@]}"; do
      echo "  -> ${file#$ROOT_DIR/}"
      if apply_file "$file"; then
        succeeded=$((succeeded + 1))
      else
        echo "     deferred"
        deferred+=("$file")
      fi
    done

    if [[ ${#deferred[@]} -eq 0 ]]; then
      break
    fi

    if [[ $succeeded -eq 0 ]]; then
      die "No progress while applying ${dir#$ROOT_DIR/}. First failing file: ${deferred[0]}"
    fi

    if [[ $pass -ge $MAX_PASSES ]]; then
      die "Exceeded MAX_PASSES=$MAX_PASSES for ${dir#$ROOT_DIR/}. Remaining file: ${deferred[0]}"
    fi

    pending=("${deferred[@]}")
  done
}

main() {
  require_cmd sqlcmd
  require_cmd sqlpackage
  require_cmd xxd
  require_cmd iconv
  require_cmd find
  require_cmd awk

  [[ -n "$DEV_SERVER" ]] || die "Set DEV_SERVER (example: localhost,1433)"
  [[ -n "$DEV_USER" ]] || die "Set DEV_USER"
  [[ -n "$DEV_PASS" ]] || die "Set DEV_PASS"
  [[ -d "$SQL_ROOT" ]] || die "SQL_ROOT does not exist: $SQL_ROOT"

  mkdir -p "$ARTIFACT_DIR"

  if [[ -n "$SOURCE_DACPAC" ]]; then
    [[ -f "$SOURCE_DACPAC" ]] || die "SOURCE_DACPAC not found: $SOURCE_DACPAC"
    echo "Using SOURCE_DACPAC: $SOURCE_DACPAC"
  else
    if [[ "$SHADOW_DATABASE" == "$DEV_DATABASE" ]]; then
      die "SHADOW_DATABASE must be different from DEV_DATABASE. Current: both are [$DEV_DATABASE]."
    fi

    if is_true "$SKIP_SHADOW_CREATE"; then
      echo "SKIP_SHADOW_CREATE=true: using existing shadow database [$SHADOW_DATABASE] on server [$DEV_SERVER]"
      local shadow_exists
      shadow_exists="$(sqlcmd -S "$DEV_SERVER" -U "$DEV_USER" -P "$DEV_PASS" -C -d master -h -1 -W -Q "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'$SHADOW_DATABASE') IS NULL THEN 0 ELSE 1 END;" | tr -d '[:space:]')"
      [[ "$shadow_exists" == "1" ]] || die "Shadow database [$SHADOW_DATABASE] does not exist. Ask DBA to create it, or run with SKIP_SHADOW_CREATE=false using a login with CREATE DATABASE permission."
    else
      echo "Creating shadow database [$SHADOW_DATABASE] on server [$DEV_SERVER]..."
      run_sql master -Q "IF DB_ID(N'$SHADOW_DATABASE') IS NOT NULL BEGIN ALTER DATABASE [$SHADOW_DATABASE] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [$SHADOW_DATABASE]; END; CREATE DATABASE [$SHADOW_DATABASE];"
    fi

    local dirs=(
      "$SQL_ROOT/Table"
      "$SQL_ROOT/Function"
      "$SQL_ROOT/View/PIRO"
      "$SQL_ROOT/View/SOLR"
      "$SQL_ROOT/PLSQL"
      "$SQL_ROOT/Airflow"
    )

    if is_true "$INCLUDE_SSIS"; then
      dirs+=(
        "$SQL_ROOT/SSIS/TABLES"
        "$SQL_ROOT/SSIS/PROCS/LOADER-PIRO"
        "$SQL_ROOT/SSIS/PROCS/LOADER-SOLR"
        "$SQL_ROOT/SSIS/PROCS/TRUNCATE"
      )
    fi

    if is_true "$INCLUDE_INDEX"; then
      dirs+=("$SQL_ROOT/Index")
    fi

    for dir in "${dirs[@]}"; do
      apply_dir_with_retries "$dir"
    done
  fi

  echo "Generating deploy report..."
  if [[ -n "$SOURCE_DACPAC" ]]; then
    sqlpackage \
      /Action:DeployReport \
      /SourceFile:"$SOURCE_DACPAC" \
      /TargetServerName:"$DEV_SERVER" \
      /TargetDatabaseName:"$DEV_DATABASE" \
      /TargetUser:"$DEV_USER" \
      /TargetPassword:"$DEV_PASS" \
      /TargetEncryptConnection:True \
      /TargetTrustServerCertificate:True \
      /DeployReportPath:"$DEPLOY_REPORT_PATH" \
      /p:DropObjectsNotInSource=False \
      /p:IgnorePermissions=True
  else
    sqlpackage \
      /Action:DeployReport \
      /SourceServerName:"$DEV_SERVER" \
      /SourceDatabaseName:"$SHADOW_DATABASE" \
      /SourceUser:"$DEV_USER" \
      /SourcePassword:"$DEV_PASS" \
      /SourceEncryptConnection:True \
      /SourceTrustServerCertificate:True \
      /TargetServerName:"$DEV_SERVER" \
      /TargetDatabaseName:"$DEV_DATABASE" \
      /TargetUser:"$DEV_USER" \
      /TargetPassword:"$DEV_PASS" \
      /TargetEncryptConnection:True \
      /TargetTrustServerCertificate:True \
      /DeployReportPath:"$DEPLOY_REPORT_PATH" \
      /p:DropObjectsNotInSource=False \
      /p:IgnorePermissions=True
  fi

  echo "Generating migration SQL script..."
  if [[ -n "$SOURCE_DACPAC" ]]; then
    sqlpackage \
      /Action:Script \
      /SourceFile:"$SOURCE_DACPAC" \
      /TargetServerName:"$DEV_SERVER" \
      /TargetDatabaseName:"$DEV_DATABASE" \
      /TargetUser:"$DEV_USER" \
      /TargetPassword:"$DEV_PASS" \
      /TargetEncryptConnection:True \
      /TargetTrustServerCertificate:True \
      /OutputPath:"$MIGRATION_SCRIPT_PATH" \
      /p:DropObjectsNotInSource=False \
      /p:IncludeTransactionalScripts=True \
      /p:BlockOnPossibleDataLoss=False \
      /p:IgnorePermissions=True
  else
    sqlpackage \
      /Action:Script \
      /SourceServerName:"$DEV_SERVER" \
      /SourceDatabaseName:"$SHADOW_DATABASE" \
      /SourceUser:"$DEV_USER" \
      /SourcePassword:"$DEV_PASS" \
      /SourceEncryptConnection:True \
      /SourceTrustServerCertificate:True \
      /TargetServerName:"$DEV_SERVER" \
      /TargetDatabaseName:"$DEV_DATABASE" \
      /TargetUser:"$DEV_USER" \
      /TargetPassword:"$DEV_PASS" \
      /TargetEncryptConnection:True \
      /TargetTrustServerCertificate:True \
      /OutputPath:"$MIGRATION_SCRIPT_PATH" \
      /p:DropObjectsNotInSource=False \
      /p:IncludeTransactionalScripts=True \
      /p:BlockOnPossibleDataLoss=False \
      /p:IgnorePermissions=True
  fi

  echo
  echo "Completed."
  echo "Deploy report : $DEPLOY_REPORT_PATH"
  echo "Migration SQL : $MIGRATION_SCRIPT_PATH"
  echo "Post-data SQL : $POST_DEPLOY_DATA_SCRIPT"
  echo
  echo "Apply migration:"
  echo "  sqlcmd -S \"$DEV_SERVER\" -U \"$DEV_USER\" -P \"***\" -C -d \"$DEV_DATABASE\" -b -i \"$MIGRATION_SCRIPT_PATH\""
  echo "Apply post-deploy data:"
  echo "  sqlcmd -S \"$DEV_SERVER\" -U \"$DEV_USER\" -P \"***\" -C -d \"$DEV_DATABASE\" -b -i \"$POST_DEPLOY_DATA_SCRIPT\""

  if is_true "$APPLY_POST_DATA"; then
    echo "APPLY_POST_DATA=true, applying post-deploy data script now..."
    run_sql "$DEV_DATABASE" -i "$POST_DEPLOY_DATA_SCRIPT"
  fi
}

main "$@"
