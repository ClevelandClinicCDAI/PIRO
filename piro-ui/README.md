# PIRO-UI

This application - `piro-ui` - acts as the user interface for the PIRO application. This is a "Single Page Application" (SPA) written using the Angular framework.

## Running on Localhost

* Navigate to the `piro-ui` directory on your computer.
  * If any new packages have been added to the `package.json` file, execute `npm install`.
* Execute `ng serve`.
* The application will now be available at [http://localhost:4201/home](http://localhost:4201/home).

### Application Install on Localhost

#### Prerequisites

* node js must be installed.

#### Steps

* Clone the codebase into a directory on your computer.
* Execute `npm install` to install the necessary packages.
* Create a configuration file - `config.json` - in the `piro-ui/src/assets` directory (next to the `config.example.json` file).  See the `config.example.json` file for an example of the file format and values.

### Runtime Configuration (`config.json`)

The Angular SPA loads `assets/config.json` at startup via
`AppConfigService`. Fields:

| Field               | Default              | Purpose                                                                                                             |
| ------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `apiBaseUrl`        | *(required)*         | Base URL of `piro-api`. All relative HTTP requests are resolved against this.                                        |
| `irbDisclaimerText` | *(required)*         | Text shown in the IRB disclaimer banner.                                                                             |
| `authMode`          | `"LDAP"`             | `"LDAP"` renders the username/password form. `"OAUTH"` renders a single-sign-on button and enables the PKCE flow. Case-insensitive. |
| `oidcIssuer`        | *(required if OAUTH)* | Issuer URL. Used to discover `authorization_endpoint`, `token_endpoint`, and `end_session_endpoint`.                 |
| `oidcClientId`      | *(required if OAUTH)* | OIDC client id registered with the IdP.                                                                              |
| `oidcRedirectUri`   | *(required if OAUTH)* | Redirect URI. Must be `<your-ui-origin>/auth/callback` and be registered with the IdP. `/auth/callback` is a public route (no `AuthGuard`). |
| `oidcScopes`        | `"openid profile email"` | Space-separated scopes requested during authorization.                                                          |

Under Docker Compose, `docker-entrypoint.sh` writes `config.json` at
container start from the `AUTH_MODE`, `OIDC_ISSUER_PUBLIC`,
`OIDC_CLIENT_ID`, `OIDC_REDIRECT_URI`, and `OIDC_SCOPES` environment
variables — no rebuild is needed to switch modes.

### Local OAuth Testing

The repo ships with a `mock-oauth` compose service. To exercise the
end-to-end SSO flow on Windows:

1. Add `127.0.0.1  piro-auth` to `%WINDIR%\System32\drivers\etc\hosts`
   so the same URL (`http://piro-auth:8888/piro`) is reachable from
   both the browser and the api container.
2. Start the stack in OAuth mode:

    ```powershell
    $env:PIRO_AUTH_MODE = "OAUTH"
    docker compose up -d
    ```

3. Browse to <http://localhost:8080/login>, click the SSO button,
   enter any username at the mock IdP (no password is required), and
   you will be redirected back to `/auth/callback` and signed in.

Logout (`POST /token/logout`) returns `{end_session_url}` in OAUTH
mode; the SPA follows that URL so the mock IdP session is terminated
as well.

## Server Deployment

### Azure DevOps Pipeline Deployment

(coming soon)

### Manual Deployment

* On localhost, from within the root of the codebase base execute `ng build --configuration=[development|production]`
  * This will generate build artifacts in the `dist` directory.
* Copy these files to the server, replacing the files in `/opt/piro-ui`.

## Server Application Installation

### Environment-Specific Configuration

Create a configuration file - `config.json` - to provide values to the application that are inappropriate for inclusion in version control.  This file should be placed within the 'assets' directory on the server where the build files are deployed (next to the `config.example.json` file).  See the `config.example.json` file for an example of the file format and values.

### Nginx Configuration

Because the `piro-ui` application consists of simple HTML/JS files, we simply serve it using the already installed NGINX web server.

* Alter the `/etc/nginx/sites-available/piro-ui` file to match the following (adjusting as needed):

    ```bash
    server {
        server_name <your domain name>;

        listen 443 ssl;

        ssl_certificate /etc/ssl/certs/<your domain name>.cer;
        ssl_certificate_key /etc/ssl/certs/<your domain name>.key;

        ssl_session_cache  builtin:1000  shared:SSL:10m;
        ssl_protocols  TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
        ssl_prefer_server_ciphers on;

        add_header Strict-Transport-Security "max-age=1209600" always;  # 2 weeks
        # use of 'unsafe-inline' in the 'script-src' directive can be removed later
        # if piro-ui is altered to avoid the use of 'javascript:void(0)' calls.
        add_header Content-Security-Policy
            "default-src 'self' <your domain name>:* *.<your domain name>:*;
            script-src 'self' 'unsafe-inline' 'unsafe-eval' <your domain name>:* *.<your domain name>:*;
            style-src 'self' 'unsafe-inline' <your domain name>:* *.<your domain name>:*;
            img-src * data:;
            frame-ancestors 'none'";
        add_header X-Frame-Options SAMEORIGIN always;
        add_header X-Content-Type-Options nosniff;

        root /opt/piro-ui;

        location / {
            try_files $uri $uri/ /index.html =404;
        }
    }
    ```

* Create a new symlink in the sites-enabled directory to enable the piro-ui nginx configuration:

    ```bash
    cd /etc/nginx/sites-enabled
    sudo ln -s /etc/nginx/sites-available/piro-ui /etc/nginx/sites-enabled/
    ```
