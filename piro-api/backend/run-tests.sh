#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTEST="${ROOT_DIR}/../.venv/bin/pytest"

if [[ ! -x "${VENV_PYTEST}" ]]; then
  echo "pytest not found at ${VENV_PYTEST}. Create the venv at piro-api/.venv first." >&2
  exit 1
fi

: "${DATABASE:=SQLITE}"
: "${ACCESS_TOKEN_EXPIRE_MINUTES:=300}"
: "${SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES:=300}"
: "${ACCESS_TOKEN_SECRET_KEY:=dev-secret}"
: "${ACCESS_TOKEN_ALGORITHM:=HS256}"
: "${AD_LDAP_PATH:=ldap://localhost}"
: "${AD_DOMAIN:=example.com}"
: "${AD_SECURITY_GROUP:=testgroup}"

export DATABASE
export ACCESS_TOKEN_EXPIRE_MINUTES
export SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES
export ACCESS_TOKEN_SECRET_KEY
export ACCESS_TOKEN_ALGORITHM
export AD_LDAP_PATH
export AD_DOMAIN
export AD_SECURITY_GROUP

cd "${ROOT_DIR}"
"${VENV_PYTEST}" -q
