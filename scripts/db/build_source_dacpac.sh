#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SQL_ROOT="${SQL_ROOT:-$ROOT_DIR/piro-sql}"
TABLE_ORDER_SCRIPT="${TABLE_ORDER_SCRIPT:-$ROOT_DIR/piro-sample-data/table_order.py}"

SOURCE_SERVER="${SOURCE_SERVER:-127.0.0.1,1433}"
SOURCE_DATABASE="${SOURCE_DATABASE:-PIRO_DACPAC_SRC}"
SOURCE_USER="${SOURCE_USER:-sa}"
SOURCE_PASS="${SOURCE_PASS:-P1ro!LocalDev}"

INCLUDE_SSIS="${INCLUDE_SSIS:-true}"

OUTPUT_DACPAC="${OUTPUT_DACPAC:-$ROOT_DIR/artifacts/db-migration/piro_source.dacpac}"
MAX_PASSES="${MAX_PASSES:-10}"

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
  sqlcmd -S "$SOURCE_SERVER" -U "$SOURCE_USER" -P "$SOURCE_PASS" -C -b -d "$database" "$@"
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

  # Strip UTF-8 BOM if present.
  awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}1' "$tmp" >"${tmp}.clean"
  mv "${tmp}.clean" "$tmp"

  if [[ "$file" == *"/SSIS/TABLES/"* ]]; then
    local base table_name
    base="$(basename "$file")"
    table_name="${base#*.}"
    table_name="${table_name%%.*}"
    run_sql "$SOURCE_DATABASE" -Q "IF OBJECT_ID('[dbo].[$table_name]', 'U') IS NOT NULL DROP TABLE [dbo].[$table_name];" >/dev/null || true
  fi

  run_sql "$SOURCE_DATABASE" -i "$tmp"
  rm -f "$tmp"
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

apply_table_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0

  local ordered=()
  if [[ -f "$TABLE_ORDER_SCRIPT" ]]; then
    while IFS= read -r file; do
      ordered+=("$file")
    done < <(python3 "$TABLE_ORDER_SCRIPT" "$dir")
  else
    while IFS= read -r file; do
      ordered+=("$file")
    done < <(find "$dir" -type f -name '*.sql' | sort)
  fi

  [[ ${#ordered[@]} -gt 0 ]] || return 0

  echo "Applying directory: ${dir#$ROOT_DIR/} (ordered)"
  for file in "${ordered[@]}"; do
    echo "  -> ${file#$ROOT_DIR/}"
    apply_file "$file"
  done
}

main() {
  require_cmd sqlcmd
  require_cmd sqlpackage
  require_cmd xxd
  require_cmd iconv
  require_cmd find
  require_cmd awk
  require_cmd python3

  [[ -d "$SQL_ROOT" ]] || die "SQL_ROOT does not exist: $SQL_ROOT"

  mkdir -p "$(dirname "$OUTPUT_DACPAC")"

  echo "Recreating source database [$SOURCE_DATABASE] on [$SOURCE_SERVER]..."
  run_sql master -Q "IF DB_ID(N'$SOURCE_DATABASE') IS NOT NULL BEGIN ALTER DATABASE [$SOURCE_DATABASE] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [$SOURCE_DATABASE]; END; CREATE DATABASE [$SOURCE_DATABASE];"

  apply_table_dir "$SQL_ROOT/Table"
  apply_dir_with_retries "$SQL_ROOT/Function"
  apply_dir_with_retries "$SQL_ROOT/View/PIRO"
  apply_dir_with_retries "$SQL_ROOT/View/SOLR"
  apply_dir_with_retries "$SQL_ROOT/PLSQL"
  apply_dir_with_retries "$SQL_ROOT/Airflow"

  if is_true "$INCLUDE_SSIS"; then
    apply_dir_with_retries "$SQL_ROOT/SSIS/TABLES"
    apply_dir_with_retries "$SQL_ROOT/SSIS/PROCS/LOADER-PIRO"
    apply_dir_with_retries "$SQL_ROOT/SSIS/PROCS/LOADER-SOLR"
    apply_dir_with_retries "$SQL_ROOT/SSIS/PROCS/TRUNCATE"
  fi

  echo "Extracting DACPAC to: $OUTPUT_DACPAC"
  sqlpackage \
    /Action:Extract \
    /SourceServerName:"$SOURCE_SERVER" \
    /SourceDatabaseName:"$SOURCE_DATABASE" \
    /SourceUser:"$SOURCE_USER" \
    /SourcePassword:"$SOURCE_PASS" \
    /SourceEncryptConnection:True \
    /SourceTrustServerCertificate:True \
    /TargetFile:"$OUTPUT_DACPAC"

  echo "Verifying DACPAC content..."
  if unzip -p "$OUTPUT_DACPAC" model.xml | rg -q -i "MICROSCOPIC"; then
    echo "Verified: MICROSCOPIC exists in DACPAC model."
  else
    die "MICROSCOPIC was not found in DACPAC model."
  fi

  echo "Done: $OUTPUT_DACPAC"
}

main "$@"
