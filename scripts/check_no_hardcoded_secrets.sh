#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="${1:-$ROOT_DIR/scripts}"

if [[ ! -d "$SCRIPTS_DIR" ]]; then
  echo "ERROR: scripts directory not found: $SCRIPTS_DIR" >&2
  exit 1
fi

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf "%s" "$value"
}

strip_quotes() {
  local value="$1"
  if [[ ${#value} -ge 2 && "${value:0:1}" == "\"" && "${value: -1}" == "\"" ]]; then
    printf "%s" "${value:1:${#value}-2}"
    return
  fi
  if [[ ${#value} -ge 2 && "${value:0:1}" == "'" && "${value: -1}" == "'" ]]; then
    printf "%s" "${value:1:${#value}-2}"
    return
  fi
  printf "%s" "$value"
}

is_safe_secret_value() {
  local raw="$1"
  local value
  value="$(trim "$raw")"

  # Remove simple inline comment from unquoted values.
  if [[ "$value" != \"* && "$value" != \'* ]]; then
    value="${value%%#*}"
    value="$(trim "$value")"
  fi

  value="$(strip_quotes "$value")"
  value="$(trim "$value")"

  [[ -z "$value" ]] && return 0
  [[ "$value" == *'$'* ]] && return 0
  [[ "$value" == \<* ]] && return 0
  [[ "$value" == \{* ]] && return 0
  [[ "$value" == \[* ]] && return 0
  return 1
}

report_violation() {
  local file="$1"
  local line_number="$2"
  local line="$3"
  echo "Hardcoded secret candidate: ${file}:${line_number}" >&2
  echo "  ${line}" >&2
}

main() {
  local failed=0
  local file

  while IFS= read -r file; do
    local line
    local line_number=0

    while IFS= read -r line || [[ -n "$line" ]]; do
      line_number=$((line_number + 1))
      local trimmed_line
      trimmed_line="$(trim "$line")"

      [[ -z "$trimmed_line" ]] && continue
      [[ "$trimmed_line" == \#* ]] && continue

      # Variable assignment: FOO_PASSWORD=...
      if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.+)$ ]]; then
        local var_name="${BASH_REMATCH[1]}"
        local var_value="${BASH_REMATCH[2]}"
        local var_name_upper
        var_name_upper="$(echo "$var_name" | tr '[:lower:]' '[:upper:]')"
        if [[ "$var_name_upper" =~ (^|_)(PASS|PASSWORD|PASSWD)(_|$) ]] \
          || [[ "$var_name_upper" =~ (^|_)(SECRET|TOKEN)(_|$) ]] \
          || [[ "$var_name_upper" =~ (^|_)(API_KEY|APIKEY|ACCESS_KEY|ACCESSKEY|PRIVATE_KEY|PRIVATEKEY)(_|$) ]] \
          || [[ "$var_name_upper" =~ (^|_)(CONNECTION_STRING|CONN_STRING|CONNSTR)(_|$) ]]; then
          if ! is_safe_secret_value "$var_value"; then
            report_violation "$file" "$line_number" "$line"
            failed=1
          fi
        fi
      fi

      # sqlcmd: -P <password>
      if [[ "$line" =~ (^|[[:space:]])-P[[:space:]]+([^[:space:]]+) ]]; then
        local cli_password="${BASH_REMATCH[2]}"
        if ! is_safe_secret_value "$cli_password"; then
          report_violation "$file" "$line_number" "$line"
          failed=1
        fi
      fi

      # sqlpackage: /SourcePassword:<password> or /TargetPassword:<password>
      if [[ "$line" =~ /(SourcePassword|TargetPassword):([^[:space:]]+) ]]; then
        local sqlpackage_password="${BASH_REMATCH[2]}"
        if ! is_safe_secret_value "$sqlpackage_password"; then
          report_violation "$file" "$line_number" "$line"
          failed=1
        fi
      fi
    done < "$file"
  done < <(find "$SCRIPTS_DIR" -type f | sort)

  if [[ "$failed" -ne 0 ]]; then
    echo >&2
    echo "Found potential hardcoded secrets in $SCRIPTS_DIR." >&2
    exit 1
  fi

  echo "No hardcoded secrets detected under $SCRIPTS_DIR."
}

main "$@"
