#!/bin/sh
set -e

cat > /usr/share/nginx/html/assets/config.json <<EOF
{
    "apiBaseUrl": "${API_BASE_URL:-/api/}",
    "irbDisclaimerText": "${IRB_DISCLAIMER_TEXT:-}",
    "authMode": "${AUTH_MODE:-LDAP}",
    "oidcIssuer": "${OIDC_ISSUER_PUBLIC:-}",
    "oidcClientId": "${OIDC_CLIENT_ID:-}",
    "oidcRedirectUri": "${OIDC_REDIRECT_URI:-}",
    "oidcScopes": "${OIDC_SCOPES:-openid profile email}"
}
EOF

exec nginx -g "daemon off;"
