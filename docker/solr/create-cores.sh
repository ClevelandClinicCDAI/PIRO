#!/bin/bash
set -euo pipefail
CONFIG_ROOT="/opt/piro-solr/V9"
for core in PIROCase PIROCohort PIROSuggestCase PIROSuggestComment PIROSuggestStaff; do
  if [ ! -d "${CONFIG_ROOT}/${core}" ]; then
    echo "Missing config for ${core} in ${CONFIG_ROOT}" >&2
    exit 1
  fi
  echo "Creating core ${core}"
  solr-precreate "${core}" "${CONFIG_ROOT}/${core}"
done
