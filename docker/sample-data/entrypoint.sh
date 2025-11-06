#!/bin/bash
set -euo pipefail
SQL_HOST=${SQLSERVER_HOST:-sqlserver}
SQL_PORT=${SQLSERVER_PORT:-1433}
SQL_USER=${SQLSERVER_USER:-sa}
SQL_PASS=${SQLSERVER_PASSWORD:-${SA_PASSWORD:-P1ro!LocalDev}}
SQL_DB=${SQLSERVER_DB:-PIRO}
BOOTSTRAP=${PIRO_BOOTSTRAP_DB:-true}
FORCE_RESET=${PIRO_FORCE_RESET:-true}
LOAD_SAMPLE=${PIRO_LOAD_SAMPLE_DATA:-false}
SOLR_URL=${SOLR_URL:-http://solr:8983/solr}
SCRIPTS_ROOT=/seed/piro-sql
SAMPLE_SQL=/seed/sample-data.sql
log(){ printf '%s\n' "$*"; }
run_sql(){
  local database=$1
  shift
  /opt/mssql-tools/bin/sqlcmd -S "${SQL_HOST},${SQL_PORT}" -U "${SQL_USER}" -P "${SQL_PASS}" -d "$database" -b "$@"
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
    local progress=0
    for file in "${pending[@]}"; do
      log "Applying ${file#/seed/}"
      if [[ "$file" == */SSIS/TABLES/* ]]; then
        local base table_name
        base=$(basename "$file")
        table_name=${base#*.}
        table_name=${table_name%%.*}
        run_sql "$SQL_DB" -Q "IF OBJECT_ID('[dbo].[$table_name]', 'U') IS NOT NULL DROP TABLE [dbo].[$table_name]" >/dev/null 2>&1 || true
      fi
      if run_sql "$SQL_DB" -i "$file"; then
        progress=1
      else
        log "Deferring ${file#/seed/}; see error above"
        deferred+=("$file")
      fi
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
seed_sql_data(){
  if [ ! -f "$SAMPLE_SQL" ]; then
    return
  fi
  if [ "$LOAD_SAMPLE" != "true" ]; then
    log "Sample data flag disabled; skipping SQL seed"
    return
  fi
  log "Loading SQL sample data"
  run_sql "$SQL_DB" -i "$SAMPLE_SQL"
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
