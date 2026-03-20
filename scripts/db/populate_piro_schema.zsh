#!/bin/zsh
set -euo pipefail

ROOT="${PIRO_ROOT:-}"
SERVER="${PIRO_DB_SERVER:-}"
DB="${PIRO_DB_NAME:-}"
DB_USER="${PIRO_DB_USER:-}"
DB_PASSWORD="${PIRO_DB_PASSWORD:-}"
MAX_PASSES=10

require_env() {
  local name=$1
  local value=$2
  if [ -z "${value}" ]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 1
  fi
}

require_dir() {
  local name=$1
  local path=$2
  if [ ! -d "${path}" ]; then
    echo "Directory from ${name} does not exist: ${path}" >&2
    exit 1
  fi
}

run_sql_file() {
  local file=$1
  sqlcmd -S ${SERVER} -d ${DB} -U ${DB_USER} -P ${DB_PASSWORD} -N -C -b -l 30 -i ${file}
}

run_sql_query() {
  local query=$1
  sqlcmd -S ${SERVER} -d ${DB} -U ${DB_USER} -P ${DB_PASSWORD} -N -C -b -l 30 -Q ${query}
}

run_sql_scalar() {
  local query=$1
  sqlcmd -S ${SERVER} -d ${DB} -U ${DB_USER} -P ${DB_PASSWORD} -N -C -b -l 30 -h -1 -W -Q "${query}" | tr -d '\r'
}

extract_table_identity_from_file() {
  local file=$1
  local base
  local schema
  local table

  base=$(basename "${file}")
  [[ "${base}" == *.Table.sql ]] || return 1
  base=${base%.Table.sql}
  schema=${base%%.*}
  table=${base#*.}

  [[ -n "${schema}" && -n "${table}" && "${table}" != "${base}" ]] || return 1
  printf '%s|%s\n' "${schema}" "${table}"
}

load_existing_table_identities() {
  run_sql_scalar "SET NOCOUNT ON; SELECT LOWER(s.name) + '|' + LOWER(t.name) FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id;"
}

apply_file() {
  local file=$1
  local tmp
  local bom
  local output
  local rc

  tmp=$(mktemp /tmp/piro_sql_XXXXXX)
  bom=$(xxd -p -l 2 ${file} | tr -d '\n')

  case ${bom} in
    fffe) iconv -f UTF-16LE -t UTF-8 ${file} > ${tmp} ;;
    feff) iconv -f UTF-16BE -t UTF-8 ${file} > ${tmp} ;;
    *) cp ${file} ${tmp} ;;
  esac

  # Some checked-in SQL files carry repeated BOM bytes in the file body.
  # Strip any leading UTF-8 BOM sequences after normalization so sqlcmd
  # does not choke on them.
  perl -0pi -e 's/^(?:\xEF\xBB\xBF)+//; s/^\s*USE\s+\[[^]]+\]\s*\r?\nGO\s*\r?\n//i' ${tmp}

  if output=$(run_sql_file ${tmp} 2>&1); then
    [ -n "${output}" ] && echo "${output}"
    rm -f ${tmp}
    return 0
  else
    rc=$?
    if echo "${output}" | grep -Eq 'Msg[[:space:]]+2714|There is already an object named'; then
      echo "${output}"
      echo '  -> skipping existing object from '${file#${ROOT}/}
      rm -f ${tmp}
      return 0
    fi

    [ -n "${output}" ] && echo "${output}" >&2
    rm -f ${tmp}
    return ${rc}
  fi
}

apply_list_with_retries() {
  local list_file=$1
  local label=$2
  local pending_file
  local deferred_file
  local pass=1

  pending_file=$(mktemp /tmp/piro_pending_XXXXXX)
  deferred_file=$(mktemp /tmp/piro_deferred_XXXXXX)
  awk '!seen[$0]++' ${list_file} > ${pending_file}

  while true; do
    echo 'Applying '${label}' (pass '${pass}')'
    : > ${deferred_file}
    local progressed=0
    local -A seen_in_pass

    while IFS= read -r file; do
      [ -n ${file:-} ] || continue
      if [[ -n ${seen_in_pass[$file]-} ]]; then
        continue
      fi
      seen_in_pass[$file]=1
      echo '  -> '${file#${ROOT}/}
      if apply_file ${file}; then
        progressed=$((progressed + 1))
      else
        echo ${file} >> ${deferred_file}
      fi
    done < ${pending_file}

    if [ ! -s ${deferred_file} ]; then
      rm -f ${pending_file} ${deferred_file}
      return 0
    fi

    if [ ${progressed} -eq 0 ]; then
      echo 'No progress while applying '${label}
      echo 'First failing file:'
      head -n 1 ${deferred_file}
      rm -f ${pending_file} ${deferred_file}
      return 1
    fi

    pass=$((pass + 1))
    if [ ${pass} -gt ${MAX_PASSES} ]; then
      echo 'Exceeded MAX_PASSES='${MAX_PASSES}' for '${label}
      echo 'First remaining file:'
      head -n 1 ${deferred_file}
      rm -f ${pending_file} ${deferred_file}
      return 1
    fi

    cp ${deferred_file} ${pending_file}
  done
}

apply_dir_with_retries() {
  local dir=$1
  local list_file

  [ -d ${dir} ] || return 0

  list_file=$(mktemp /tmp/piro_list_XXXXXX)
  build_sql_file_list ${dir} | awk '!seen[$0]++' > ${list_file}

  if [ ! -s ${list_file} ]; then
    rm -f ${list_file}
    return 0
  fi

  apply_list_with_retries ${list_file} ${dir#${ROOT}/}
  rm -f ${list_file}
}

build_sql_file_list() {
  local dir=$1
  local file
  local -a prioritized_files
  local -A emitted_files

  if [[ ${dir} == ${ROOT}/piro-sql/View/PIRO ]]; then
    prioritized_files=(
      ${dir}/dbo.V_Patient.View.sql
      ${dir}/dbo.V_Patient_Hash.View.sql
      ${dir}/dbo.V_Hospital.View.sql
      ${dir}/dbo.V_Interpreter.View.sql
      ${dir}/dbo.V_InterpreterAll.View.sql
      ${dir}/dbo.V_Specimen.View.sql
      ${dir}/dbo.V_SpecimenAll.View.sql
      ${dir}/dbo.V_CaseCommentCopath.View.sql
      ${dir}/dbo.V_CaseCommentEpic.View.sql
      ${dir}/dbo.V_CaseCommentText.View.sql
      ${dir}/dbo.V_CaseComment.View.sql
      ${dir}/dbo.V_CaseComment_Consolidated.View.sql
      ${dir}/dbo.V_CaseStaff.View.sql
      ${dir}/dbo.V_CaseStaffAll.View.sql
      ${dir}/dbo.V_Case_MRN.View.sql
      ${dir}/dbo.V_Case.View.sql
      ${dir}/dbo.V_CaseAll.View.sql
      ${dir}/dbo.V_CaseAll_Consolidated.View.sql
      ${dir}/dbo.V_AuditTrail_Report.View.sql
      ${dir}/dbo.V_SearchRequest.View.sql
    )

    for file in ${prioritized_files}; do
      if [ -f ${file} ]; then
        echo "${file}"
        emitted_files[${file}]=1
      fi
    done

    while IFS= read -r file; do
      if [[ -z ${emitted_files[$file]-} ]]; then
        echo "${file}"
      fi
    done < <(find ${dir} -type f -name '*.sql' | sort)
    return 0
  fi

  find ${dir} -type f -name '*.sql' | sort
}

apply_tables_with_retries() {
  local table_dir=${ROOT}/piro-sql/Table
  local list_file
  local unique_file
  local filtered_file
  local existing_tables_file
  local existing_identity_count=0
  local filtered_count=0

  list_file=$(mktemp /tmp/piro_tables_XXXXXX)
  unique_file=$(mktemp /tmp/piro_tables_unique_XXXXXX)
  filtered_file=$(mktemp /tmp/piro_tables_filtered_XXXXXX)
  existing_tables_file=$(mktemp /tmp/piro_tables_existing_XXXXXX)

  if [ -f ${ROOT}/piro-sample-data/table_order.py ]; then
    python3 ${ROOT}/piro-sample-data/table_order.py ${table_dir} > ${list_file}
  else
    find ${table_dir} -type f -name '*.sql' | sort > ${list_file}
  fi

  awk '!seen[$0]++' ${list_file} > ${unique_file}
  load_existing_table_identities | awk 'NF { print tolower($0) }' > ${existing_tables_file}
  if [ -s ${existing_tables_file} ]; then
    existing_identity_count=$(wc -l < ${existing_tables_file} | tr -d ' ')
  fi

  while IFS= read -r file; do
    local identity
    local identity_lc
    [ -n ${file:-} ] || continue
    identity=$(extract_table_identity_from_file "${file}") || identity=''
    identity_lc=$(echo "${identity}" | tr '[:upper:]' '[:lower:]')
    if [ -n "${identity_lc}" ] && [ -s ${existing_tables_file} ] && grep -Fxq "${identity_lc}" ${existing_tables_file}; then
      echo '  -> skipping existing table '${file#${ROOT}/}
      continue
    fi
    echo "${file}" >> ${filtered_file}
    filtered_count=$((filtered_count + 1))
  done < ${unique_file}

  echo 'Detected '${existing_identity_count}' existing tables in target database'
  echo 'Pending table scripts to apply: '${filtered_count}

  if [ -s ${filtered_file} ]; then
    apply_list_with_retries ${filtered_file} 'piro-sql/Table'
  else
    echo 'All table scripts already exist; skipping piro-sql/Table'
  fi

  rm -f ${list_file} ${unique_file} ${filtered_file} ${existing_tables_file}
}

main() {
  require_env 'PIRO_ROOT' "${ROOT}"
  require_dir 'PIRO_ROOT' "${ROOT}"
  require_env 'PIRO_DB_SERVER' "${SERVER}"
  require_env 'PIRO_DB_NAME' "${DB}"
  require_env 'PIRO_DB_USER' "${DB_USER}"
  require_env 'PIRO_DB_PASSWORD' "${DB_PASSWORD}"

  echo 'Target server: '${SERVER}
  echo 'Target database: '${DB}
  echo 'Applying schema from: '${ROOT}

  apply_tables_with_retries

  apply_dir_with_retries ${ROOT}/piro-sql/Function
  apply_dir_with_retries ${ROOT}/piro-sql/View/PIRO
  apply_dir_with_retries ${ROOT}/piro-sql/View/SOLR
  apply_dir_with_retries ${ROOT}/piro-sql/PLSQL
  apply_dir_with_retries ${ROOT}/piro-sql/Airflow
  apply_dir_with_retries ${ROOT}/piro-sql/SSIS/TABLES
  apply_dir_with_retries ${ROOT}/piro-sql/SSIS/PROCS/LOADER-PIRO
  apply_dir_with_retries ${ROOT}/piro-sql/SSIS/PROCS/LOADER-SOLR
  apply_dir_with_retries ${ROOT}/piro-sql/SSIS/PROCS/TRUNCATE

  echo 'Done. Object counts:'
  run_sql_query 'SET NOCOUNT ON; SELECT (SELECT COUNT(*) FROM sys.tables) AS table_count, (SELECT COUNT(*) FROM sys.views) AS view_count, (SELECT COUNT(*) FROM sys.procedures) AS procedure_count;'
}

main
