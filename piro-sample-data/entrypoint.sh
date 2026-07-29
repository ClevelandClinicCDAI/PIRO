#!/bin/bash
set -euo pipefail

if [ "${BASH_VERSINFO[0]:-0}" -lt 4 ]; then
  printf 'seed.sh requires bash 4.0 or newer (found %s)\n' "${BASH_VERSINFO[0]:-unknown}" >&2
  exit 1
fi
SQL_HOST=${SQLSERVER_HOST:-sqlserver}
SQL_PORT=${SQLSERVER_PORT:-1433}
SQL_USER=${SQLSERVER_USER:-sa}
SQL_PASS=${SQLSERVER_PASSWORD:-${SA_PASSWORD:-P1ro!LocalDev}}
SQL_DB=${SQLSERVER_DB:-PIRO}
BOOTSTRAP=${PIRO_BOOTSTRAP_DB:-true}
FORCE_RESET=${PIRO_FORCE_RESET:-true}
LOAD_SAMPLE=${PIRO_LOAD_SAMPLE_DATA:-false}
SOLR_URL=${SOLR_URL:-http://solr:8983/solr}
SAMPLE_USER_NUID=${PIRO_SAMPLE_USER_NUID:-}
SAMPLE_USER_FIRST_NAME=${PIRO_SAMPLE_USER_FIRST_NAME:-}
SAMPLE_USER_LAST_NAME=${PIRO_SAMPLE_USER_LAST_NAME:-}
SAMPLE_USER_ROLE=${PIRO_SAMPLE_USER_ROLE:-}
SCRIPTS_ROOT=/seed/piro-sql
SAMPLE_SQL=/seed/sample-data.sql
log(){ printf '%s\n' "$*"; }
escape_sql_var(){
  local value="$1"
  value=${value//\"/\"\"}
  printf '%s' "$value"
}
run_sql(){
  local database=$1
  shift
  /opt/mssql-tools/bin/sqlcmd -S "${SQL_HOST},${SQL_PORT}" -U "${SQL_USER}" -P "${SQL_PASS}" -d "$database" -b "$@"
}
normalize_sql_file(){
  local file=$1
  local tmp
  local bom

  tmp=$(mktemp)
  bom=$(xxd -p -l 2 "$file" | tr -d '\n')

  case "$bom" in
    fffe) iconv -f UTF-16LE -t UTF-8 "$file" > "$tmp" ;;
    feff) iconv -f UTF-16BE -t UTF-8 "$file" > "$tmp" ;;
    *) cp "$file" "$tmp" ;;
  esac

  perl -0pi -e 's/^(?:\xEF\xBB\xBF)+//; s/^\s*USE\s+\[[^]]+\]\s*\r?\nGO\s*\r?\n//i' "$tmp"
  printf '%s\n' "$tmp"
}
wait_for_sql(){
  local attempts=0
  until run_sql master -Q "SELECT 1" >/dev/null 2>&1; do
    attempts=$((attempts+1))
    if [ $attempts -gt 60 ]; then
      log "SQL Server did not become ready in time"
      exit 1
    fi
    sleep 2
  done
}
apply_dir(){
  local dir=$1
  if [ ! -d "$dir" ]; then
    return
  fi
  if [ "$dir" = "${SCRIPTS_ROOT}/Table" ] && [ -x /usr/local/bin/table-order.py ]; then
    if ! mapfile -t files < <(python3 /usr/local/bin/table-order.py "$dir"); then
      log "Falling back to alphabetical order for $dir"
      mapfile -t files < <(find "$dir" -type f -name '*.sql' | sort)
    fi
  elif [ "$dir" = "${SCRIPTS_ROOT}/View/PIRO" ]; then
    mapfile -t files < <(ordered_piro_view_files "$dir")
  else
    mapfile -t files < <(find "$dir" -type f -name '*.sql' | sort)
  fi
  if [ ${#files[@]} -eq 0 ]; then
    return
  fi
  local pending=()
  pending=("${files[@]}")
  local deferred=()
  local pass=1
  while [ ${#pending[@]} -gt 0 ]; do
    deferred=()
    for file in "${pending[@]}"; do
      log "Applying ${file#/seed/}"
      local sql_input
      sql_input=$(normalize_sql_file "$file")
      if [[ "$file" == */SSIS/TABLES/* ]]; then
        local base table_name
        base=$(basename "$file")
        table_name=${base#*.}
        table_name=${table_name%%.*}
        run_sql "$SQL_DB" -Q "IF OBJECT_ID('[dbo].[$table_name]', 'U') IS NOT NULL DROP TABLE [dbo].[$table_name]" >/dev/null 2>&1 || true
      fi
      if ! run_sql "$SQL_DB" -i "$sql_input"; then
        log "Deferring ${file#/seed/}; see error above"
        deferred+=("$file")
      fi
      rm -f "$sql_input"
    done
    if [ ${#deferred[@]} -eq ${#pending[@]} ]; then
      log "Failed to apply scripts in $dir"
      exit 1
    fi
    if [ ${#deferred[@]} -gt 0 ]; then
      pending=("${deferred[@]}")
    else
      pending=()
    fi
    pass=$((pass+1))
    if [ $pass -gt 10 ]; then
      log "Exceeded retry attempts for scripts in $dir"
      exit 1
    fi
  done
}

ordered_piro_view_files(){
  local dir=$1
  local file
  local prioritized=(
    "$dir/dbo.V_Patient.View.sql"
    "$dir/dbo.V_Patient_Hash.View.sql"
    "$dir/dbo.V_Hospital.View.sql"
    "$dir/dbo.V_Interpreter.View.sql"
    "$dir/dbo.V_InterpreterAll.View.sql"
    "$dir/dbo.V_Specimen.View.sql"
    "$dir/dbo.V_SpecimenAll.View.sql"
    "$dir/dbo.V_CaseCommentCopath.View.sql"
    "$dir/dbo.V_CaseCommentEpic.View.sql"
    "$dir/dbo.V_CaseCommentText.View.sql"
    "$dir/dbo.V_CaseComment.View.sql"
    "$dir/dbo.V_CaseComment_Consolidated.View.sql"
    "$dir/dbo.V_CaseStaff.View.sql"
    "$dir/dbo.V_CaseStaffAll.View.sql"
    "$dir/dbo.V_Case_MRN.View.sql"
    "$dir/dbo.V_Case.View.sql"
    "$dir/dbo.V_CaseAll.View.sql"
    "$dir/dbo.V_CaseAll_Consolidated.View.sql"
    "$dir/dbo.V_AuditTrail_Report.View.sql"
    "$dir/dbo.V_SearchRequest.View.sql"
  )
  declare -A emitted=()

  for file in "${prioritized[@]}"; do
    if [ -f "$file" ]; then
      printf '%s\n' "$file"
      emitted["$file"]=1
    fi
  done

  while IFS= read -r file; do
    if [ -z "${emitted[$file]:-}" ]; then
      printf '%s\n' "$file"
    fi
  done < <(find "$dir" -type f -name '*.sql' | sort)
}
apply_reference_data(){
  # Reference/lookup data (e.g. dropdown terminology values) that must always be
  # present regardless of PIRO_LOAD_SAMPLE_DATA. These scripts live under MISC/
  # but, unlike other one-off MISC scripts, are written to be idempotent
  # (IF NOT EXISTS guards) and are safe/expected to run on every bootstrap.
  local reference_scripts=(
    "${SCRIPTS_ROOT}/MISC/CytologyTerminology_Seed.sql"
  )
  local file
  for file in "${reference_scripts[@]}"; do
    if [ ! -f "$file" ]; then
      continue
    fi
    log "Applying ${file#/seed/}"
    local sql_input
    sql_input=$(normalize_sql_file "$file")
    run_sql "$SQL_DB" -i "$sql_input"
    rm -f "$sql_input"
  done
}
seed_sql_data(){
  if [ ! -f "$SAMPLE_SQL" ]; then
    return
  fi
  if [ "$LOAD_SAMPLE" != "true" ]; then
    log "Sample data flag disabled; skipping SQL seed"
    return
  fi
  log "Loading SQL sample data"
  local nuid_value="${SAMPLE_USER_NUID:-__unset__}"
  local first_name_value="${SAMPLE_USER_FIRST_NAME:-__unset__}"
  local last_name_value="${SAMPLE_USER_LAST_NAME:-__unset__}"
  local role_value="${SAMPLE_USER_ROLE:-__unset__}"
  local tmp_sql
  tmp_sql=$(mktemp)
  trap 'rm -f "$tmp_sql"' RETURN
  {
    printf ':setvar SAMPLE_USER_NUID "%s"\n' "$(escape_sql_var "$nuid_value")"
    printf ':setvar SAMPLE_USER_FIRST_NAME "%s"\n' "$(escape_sql_var "$first_name_value")"
    printf ':setvar SAMPLE_USER_LAST_NAME "%s"\n' "$(escape_sql_var "$last_name_value")"
    printf ':setvar SAMPLE_USER_ROLE "%s"\n' "$(escape_sql_var "$role_value")"
    cat "$SAMPLE_SQL"
  } >"$tmp_sql"
  run_sql "$SQL_DB" -i "$tmp_sql"
  rm -f "$tmp_sql"
  trap - RETURN
}
wait_for_solr(){
  local attempts=0
  until curl -sf "${SOLR_URL}/admin/cores?action=STATUS" >/dev/null 2>&1; do
    attempts=$((attempts+1))
    if [ $attempts -gt 60 ]; then
      log "Solr did not become ready"
      return 1
    fi
    sleep 2
  done
  return 0
}
post_solr(){
  local core=$1
  local file=$2
  if [ "$LOAD_SAMPLE" != "true" ]; then
    return
  fi
  if [ ! -f "$file" ]; then
    return
  fi
  log "Seeding Solr core ${core} with $(basename "$file")"
  if ! curl -sf -X POST -H 'Content-Type: application/json' "${SOLR_URL}/${core}/update?commit=true" --data-binary "@$file" >/dev/null; then
    log "Warning: failed to seed ${core}; continuing without Solr sample docs"
  fi
}
main(){
  if [ "$BOOTSTRAP" != "true" ]; then
    log "Bootstrap disabled; exiting"
    exit 0
  fi
  wait_for_sql
  if [ "$FORCE_RESET" = "true" ]; then
    log "Resetting database ${SQL_DB}"
    run_sql master -Q "IF DB_ID('${SQL_DB}') IS NOT NULL BEGIN ALTER DATABASE [${SQL_DB}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [${SQL_DB}]; END"
  fi
  log "Creating database ${SQL_DB}"
  run_sql master -Q "IF DB_ID('${SQL_DB}') IS NULL CREATE DATABASE [${SQL_DB}]"
  for dir in Table Function View/PIRO View/SOLR PLSQL Airflow; do
    apply_dir "${SCRIPTS_ROOT}/${dir}"
  done
  apply_reference_data
  seed_sql_data
  if wait_for_solr; then
    post_solr PIROCase /seed/solr-case-docs.json
    post_solr PIROCohort /seed/solr-cohort-docs.json
    post_solr PIROSuggestCase /seed/solr-suggest-case.json
    post_solr PIROSuggestComment /seed/solr-suggest-comment.json
    post_solr PIROSuggestStaff /seed/solr-suggest-staff.json
  fi
  log "Bootstrap completed"
}
main
