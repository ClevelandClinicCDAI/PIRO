#!/bin/sh
set -e

cat > /usr/share/nginx/html/assets/config.json <<EOF
{
    "apiBaseUrl": "${API_BASE_URL:-/api/}",
    "irbDisclaimerText": "${IRB_DISCLAIMER_TEXT:-}"
}
EOF

exec nginx -g "daemon off;"
