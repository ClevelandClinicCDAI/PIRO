#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
ROOT_DIR="${PIRO_ROOT:-$(cd "$(dirname "$SCRIPT_PATH")/../.." && pwd)}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$ROOT_DIR/artifacts/db-migration/$(date +%Y%m%d_%H%M%S)}"

# Canonical names align with populate_piro_schema.zsh.
PIRO_SHADOW_DB_SERVER="${PIRO_SHADOW_DB_SERVER:-${PIRO_DB_SERVER:-}}"
PIRO_SHADOW_DB_NAME="${PIRO_SHADOW_DB_NAME:-}"
PIRO_SHADOW_DB_USER="${PIRO_SHADOW_DB_USER:-${PIRO_DB_USER:-}}"
PIRO_SHADOW_DB_PASSWORD="${PIRO_SHADOW_DB_PASSWORD:-${PIRO_DB_PASSWORD:-}}"
PIRO_SHADOW_DACPAC="${PIRO_SHADOW_DACPAC:-}"

PIRO_DB_SERVER="${PIRO_DB_SERVER:-}"
PIRO_DB_NAME="${PIRO_ESTABLISHED_DB_NAME:-}"
PIRO_DB_USER="${PIRO_DB_USER:-}"
PIRO_DB_PASSWORD="${PIRO_DB_PASSWORD:-}"

DEPLOY_REPORT_PATH="${DEPLOY_REPORT_PATH:-$ARTIFACT_DIR/shadow_vs_dev.deployreport.xml}"
MIGRATION_SCRIPT_PATH="${MIGRATION_SCRIPT_PATH:-$ARTIFACT_DIR/shadow_vs_dev.diff.sql}"
EXTRACTED_SHADOW_DACPAC_PATH="${EXTRACTED_SHADOW_DACPAC_PATH:-$ARTIFACT_DIR/shadow_source.dacpac}"

DROP_OBJECTS_NOT_IN_SHADOW="${DROP_OBJECTS_NOT_IN_SHADOW:-false}"
IGNORE_PERMISSIONS="${IGNORE_PERMISSIONS:-true}"
BLOCK_ON_POSSIBLE_DATA_LOSS="${BLOCK_ON_POSSIBLE_DATA_LOSS:-true}"
GENERATE_SMART_DEFAULTS="${GENERATE_SMART_DEFAULTS:-true}"
INCLUDE_TRANSACTIONAL_SCRIPTS="${INCLUDE_TRANSACTIONAL_SCRIPTS:-true}"

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
  require_cmd sqlpackage

  require_env "PIRO_DB_SERVER" "$PIRO_DB_SERVER"
  require_env "PIRO_DB_NAME" "$PIRO_DB_NAME"
  require_env "PIRO_DB_USER" "$PIRO_DB_USER"
  require_env "PIRO_DB_PASSWORD" "$PIRO_DB_PASSWORD"

  mkdir -p "$ARTIFACT_DIR"
  mkdir -p "$(dirname "$DEPLOY_REPORT_PATH")"
  mkdir -p "$(dirname "$MIGRATION_SCRIPT_PATH")"

  local effective_shadow_dacpac
  if [[ -n "$PIRO_SHADOW_DACPAC" ]]; then
    [[ -f "$PIRO_SHADOW_DACPAC" ]] || die "PIRO_SHADOW_DACPAC not found: $PIRO_SHADOW_DACPAC"
    effective_shadow_dacpac="$PIRO_SHADOW_DACPAC"
    echo "Using shadow DACPAC: $effective_shadow_dacpac"
    if [[ -n "$PIRO_SHADOW_DB_NAME" ]]; then
      echo "Source database (shadow): $PIRO_SHADOW_DB_NAME"
    fi
  else
    require_env "PIRO_SHADOW_DB_SERVER or PIRO_DB_SERVER" "$PIRO_SHADOW_DB_SERVER"
    require_env "PIRO_SHADOW_DB_NAME" "$PIRO_SHADOW_DB_NAME"
    require_env "PIRO_SHADOW_DB_USER or PIRO_DB_USER" "$PIRO_SHADOW_DB_USER"
    require_env "PIRO_SHADOW_DB_PASSWORD or PIRO_DB_PASSWORD" "$PIRO_SHADOW_DB_PASSWORD"
    effective_shadow_dacpac="$EXTRACTED_SHADOW_DACPAC_PATH"

    echo "Source database (shadow): $PIRO_SHADOW_DB_NAME"
    echo "Extracting shadow DACPAC from [$PIRO_SHADOW_DB_SERVER/$PIRO_SHADOW_DB_NAME]..."
    sqlpackage \
      /Action:Extract \
      /SourceServerName:"$PIRO_SHADOW_DB_SERVER" \
      /SourceDatabaseName:"$PIRO_SHADOW_DB_NAME" \
      /SourceUser:"$PIRO_SHADOW_DB_USER" \
      /SourcePassword:"$PIRO_SHADOW_DB_PASSWORD" \
      /SourceEncryptConnection:True \
      /SourceTrustServerCertificate:True \
      /TargetFile:"$effective_shadow_dacpac" \
      /OverwriteFiles:True
  fi

  echo "Comparison target database: $PIRO_DB_NAME"
  echo "Diffing shadow DACPAC [$effective_shadow_dacpac] -> target [$PIRO_DB_SERVER/$PIRO_DB_NAME]"

  echo "Generating deploy report..."
  sqlpackage \
    /Action:DeployReport \
    /SourceFile:"$effective_shadow_dacpac" \
    /TargetServerName:"$PIRO_DB_SERVER" \
    /TargetDatabaseName:"$PIRO_DB_NAME" \
    /TargetUser:"$PIRO_DB_USER" \
    /TargetPassword:"$PIRO_DB_PASSWORD" \
    /TargetEncryptConnection:True \
    /TargetTrustServerCertificate:True \
    /OutputPath:"$DEPLOY_REPORT_PATH" \
    /p:DropObjectsNotInSource="$DROP_OBJECTS_NOT_IN_SHADOW" \
    /p:IgnorePermissions="$IGNORE_PERMISSIONS" \
    /p:GenerateSmartDefaults="$GENERATE_SMART_DEFAULTS" \
    /p:BlockOnPossibleDataLoss="$BLOCK_ON_POSSIBLE_DATA_LOSS"

  echo "Generating migration script..."
  sqlpackage \
    /Action:Script \
    /SourceFile:"$effective_shadow_dacpac" \
    /TargetServerName:"$PIRO_DB_SERVER" \
    /TargetDatabaseName:"$PIRO_DB_NAME" \
    /TargetUser:"$PIRO_DB_USER" \
    /TargetPassword:"$PIRO_DB_PASSWORD" \
    /TargetEncryptConnection:True \
    /TargetTrustServerCertificate:True \
    /OutputPath:"$MIGRATION_SCRIPT_PATH" \
    /p:DropObjectsNotInSource="$DROP_OBJECTS_NOT_IN_SHADOW" \
    /p:IgnorePermissions="$IGNORE_PERMISSIONS" \
    /p:GenerateSmartDefaults="$GENERATE_SMART_DEFAULTS" \
    /p:IncludeTransactionalScripts="$INCLUDE_TRANSACTIONAL_SCRIPTS" \
    /p:BlockOnPossibleDataLoss="$BLOCK_ON_POSSIBLE_DATA_LOSS"

  echo
  echo "Completed."
  echo "Shadow DACPAC : $effective_shadow_dacpac"
  echo "Deploy report : $DEPLOY_REPORT_PATH"
  echo "Diff script   : $MIGRATION_SCRIPT_PATH"
}

main "$@"
