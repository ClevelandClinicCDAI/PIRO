# Introduction

This application - `piro-api` - is the back-end Python/FastAPI application that serves up data to the Angular front-end of the PIRO application.

## Running On localhost

* Activate the 'venv' for the project
* Navigate to the `piro-api/backend` directory
* Execute the following:

    ```bash
    uvicorn main:app --reload --port=8001
    ```

* You can then access the API via this url: <http://localhost:8001/docs>.

## Authentication Configuration

`piro-api` supports two authentication back-ends, selected at
process-start time by the `AUTH_MODE` environment variable
(case-insensitive; defaults to `LDAP`).

### AUTH_MODE=LDAP (default)

The `/token/token` endpoint accepts `{username, password, islog}`,
binds against Active Directory using the `AD_*` variables, and mints a
PIRO JWT on success. This is the pre-existing flow — no configuration
changes are required to keep it working.

Relevant variables:

| Variable | Purpose |
| :---- | :---- |
| `AD_LDAP_PATH` | LDAP URL (e.g. `ldap://ad.corp.example`). |
| `AD_DOMAIN` | AD domain used to build the bind DN. |
| `AD_SECURITY_GROUP` | Group membership required for access. |

### AUTH_MODE=OAUTH

The `/token/token` endpoint accepts `{id_token, islog}` instead. The
API validates the id_token's signature against the IdP's JWKS,
enforces issuer / audience / expiry / group-membership rules, and
mints a PIRO JWT from the token's claims. The browser SPA (see
`piro-ui/README.md`) drives the authorization-code + PKCE flow and
posts the resulting id_token to this endpoint. `POST /token/logout`
returns `{end_session_url}` — non-null only in OAUTH mode — so the
SPA can perform IdP-side single-logout.

| Variable | Default | Purpose |
| :---- | :---- | :---- |
| `OIDC_ISSUER` | *(unset)* | Issuer URL published in the id_token's `iss` claim. Also used to discover `end_session_endpoint` via `/.well-known/openid-configuration`. |
| `OIDC_AUDIENCE` | *(unset)* | Expected `aud` claim. When empty, audience validation is disabled (`verify_aud=False`). |
| `OIDC_JWKS_URL` | *(derived)* | JWKS endpoint. If unset, `oauth_auth` derives it from `OIDC_ISSUER` via discovery. |
| `OIDC_ALGORITHMS` | `RS256` | Comma-separated list of accepted JWS algorithms. |
| `OIDC_ALLOWED_GROUPS` | *(empty)* | Comma-separated allowed groups. Empty **disables** the group check (any authenticated user passes). Non-empty uses OR semantics — one match is enough. Case-insensitive. |
| `OIDC_NUID_CLAIM` | `preferred_username` | Claim used as the PIRO `nuid` (user identifier). |
| `OIDC_GIVEN_NAME_CLAIM` | `given_name` | Claim used for `firstName`. Falls back to splitting `name` on whitespace when both name claims are absent. |
| `OIDC_FAMILY_NAME_CLAIM` | `family_name` | Claim used for `lastName`. See fallback note above. |
| `OIDC_GROUPS_CLAIM` | `groups` | Claim inspected for group membership. May be a JSON array or a single string. |
| `OIDC_CLOCK_SKEW_SECONDS` | `60` | Leeway applied to `exp`/`nbf`/`iat` during signature validation. |
| `OAUTH_AUTO_PROVISION_USERS` | `false` | Hardening switch for just-in-time PIRO user creation during OAuth login. Default `false` means OAuth logins must map to an existing PIRO user row; missing users are rejected instead of auto-created. |

Sample values for the bundled `mock-oauth` compose service (see
`docker-compose.yml`) are already wired in when you run
`PIRO_AUTH_MODE=OAUTH docker compose up`.

### Executing Unit Tests

* Activate the 'venv' for the project
* Navigate to the `piro-api/backend` directory
* Execute the following: `pytest`
  * Or, to run with coverage reporting:

    ```bash
    coverage run --omit="*/tests/*" -m pytest
    ```

  * Or, to run a specific test file:

    ```bash
    pytest -s ./tests/<path/to/file>.py

    # example:
    pytest -s ./tests/test_routes/test_solr.py
    ```

  * The OAuth provider is covered by
    `tests/test_core/test_oauth_auth.py`. Those tests are pure /
    mock-based (they override the DB-bootstrap fixture, so they do
    **not** need the sqlite scaffolding or sample-data JSON files) and
    can also be executed inside the running api container:

    ```powershell
    docker exec -w /app piro-github-api-1 python -m pytest tests/test_core/test_oauth_auth.py -v
    ```

### Application Install on Localhost

#### General Prerequisites

* A modern (v3 or greater) installation of Python.

#### Installation

> Note that these instructions are for Windows

Perform all the following at a Powershell prompt:

* Create a `codebase` directory within your home folder if it doesn't already exist.
* Create a directory for the application: `..\codebase\piro-api`, and navigate to that directory.
* Create a 'venv' for the application:

    ```bash
    py -m venv piro-api_venv
    ```

* Activate the 'venv' (note that you will need to do this each time you run the application).

    ```bash
    piro-api_venv\Scripts\activate
    ```

  * The Powershell prompt should now be prefixed with the 'venv' name.
* Create a folder to contain the codebase, also named `piro-api`
  * When finished, the directory structure should look as follows:

    ```bash
    \codebase
        \piro-api
            \piro-api
            \piro-api_venv
    ```

* Navigate to the `codebase\piro-api\piro-api` directory and check out the codebase from our git repository:
  * Note the '.' at the end... important.

    ```bash
    git clone <repository URL> .
    ```

* Install necessary libraries. Execute `pip install -r core_requirements.txt` and `pip install -r dev_requirements.txt` from the root of the project.

  * If you are running on Windows, the `python-ldap` library cannot be installed via typical `pip install` commands.  Execute the following instead:
    * Navigate, on the command line, to the '_packages' folder in the codebase
    * Execute the following to install the `python_ldap` library:

    ```bash
    pip install .\python_ldap-3.4.0-cp311-cp311-win_amd64.whl
    ```

## Server Deployment

## Application Install on Our Servers

### General Prerequisites - Server

* You must have sudo access on the server where the app will be installed.
* The server must have the following packages installed:
  * System Libraries.  Execute the following:

      ```bash
      sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
      ```

  * Python version 3.11 (or newer)
    * Execute the following to install it:

      ```bash
      sudo apt update && sudo apt upgrade
      sudo add-apt-repository ppa:deadsnakes/ppa
      sudo apt install python3.11 python3.11-dev python3.11-venv
      ```

    * The new python executable should then be available as `python3.11`
  * OpenSSL version 1.1.1k (or newer)
    * You will need to upgrade OpenSSL if it doesn't meet the version requirements.  Take the following steps to do so (do all of the following as the root account):
      * Install required packages:

          ```bash
          apt update
          apt upgrade
          apt install make build-essential checkinstall zlib1g-dev
          ```

      * Remove the older version of OpenSSL installed via Apt:

        ```bash
        apt-get remove openssl
        ```

      * Download, compile, and install a newer version of OpenSSL:

        ```bash
        cd /usr/local/src
        wget --no-check-certificate https://www.openssl.org/source/old/1.1.1/openssl-1.1.1k.tar.gz
        tar -xvf openssl-1.1.1k.tar.gz
        cd openssl-1.1.1k
        ./config --prefix=/usr/local/ --openssldir=/usr/local/openssl
        make
        make test
        make install
        ```

      * Configure OpenSSL:
        * Navigate to `/etc/ld.so.conf.d`, and create a file named `openssl-1.1.1k.conf` containing the following text:

          ```bash
          /usr/local/openssl/lib
          ```

        * Finally, execute the following:

          ```bash
          ldconfig -v
          ```

      * To test the new OpenSSL: `openssl version`

  * Nginx
  * MSODBC drivers to allow connections to MS SQL Server Databases.  See <https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15&tabs=ubuntu18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Cubuntu-offline> for instructions.  Versions 17 and 18 were both tested and worked.
* A proper domain name (matching SSL/TLS certs) should have been configured for the server.
* SSL/TLS certificates should have been generated and should be available on the server.
* Create a new record in PAM/Thycotic for the dedicated 'piro-user' account.

### Installation Steps

1. Set up a dedicated user to run the app under (for security)
    * Create the user, using the password created during the prerequisites.

      ```bash
      sudo adduser piro-user
      ```

    * Grant 'sudo' access to the new 'piro-user' account.

        ```bash
        sudo gpasswd -a piro-user sudo
        ```

    * Switch to using the new account for the rest of these installs:

        ```bash
        su - piro-user
        ```

2. Create folders for the applications and set permissions:

    ```bash
    cd /opt
    sudo mkdir piro-api
    sudo chown piro-user piro-api
    sudo chgrp gs-cc-administrators piro-api

    sudo mkdir piro-ui
    sudo chown piro-user piro-ui
    sudo chgrp gs-cc-administrators piro-ui
    ```

3. Navigate into the new 'piro-api' folder:

    ```bash
    cd /opt/piro-api
    ```

4. Create a 'venv' for the application.

    ```bash
    python3.11 -m venv piro-api_venv
    ```

    * This will create a directory at `/opt/piro/piro-api_venv` where all of the venv files will reside.
5. Clone the application repo.
    * Create a nested 'piro-api' folder and navigate into it:

        ```bash
        mkdir piro-api
        cd piro-api
        ```

    * Clone the git repo (note the "." at the end... important):

        ```bash
        git clone https://ClevelandClinic@dev.azure.com/ClevelandClinic/PLMI-PIRO/_git/piro-api .
        ```

6. Install python packages
    * Activate the venv (should prefix the command prompt with 'piro-api_venv')

        ```bash
        source ../piro-api_venv/bin/activate
        ```

    * Install necessary packages via `pip`

        ```bash
        pip install -f backend/requirements.server.txt
        ```

    * Create a `.env` configuration file:
        * Within the `/opt/piro-api/piro-api/backend` directory create a file named `.env` based on the `.env.template` file from the codebase, entering values as necessary.
    * With that done, the codebase will be deployed to the folder `/opt/piro-api/piro-api`.  Naviagate to the `backend` directory and start the application by executing the following: `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --error-logfile /var/log/gunicorn/error.log --bind 0.0.0.0:8000`

7. Configure Nginx as a reverse proxy
    * If necessary, move the certificate and key to the `/etc/ssl/certs/` directory, with names to match what's included in the config file below.
    * Navigate to the nginx 'sites-enabled' directory and disable any currently available sites.
        * Example:

            ```bash
            cd /etc/nginx/sites-enabled
            sudo rm default
            ```

    * Create new nginx config files for the `piro-api`, `piro-ui`, and `solr`/`solr2` applications:
        * Navigate to the sites-available directory:

            ```bash
            cd /etc/nginx/sites-available
            ```

        * Create a new file named 'piro-api' containing the following (e.g.: `sudo nano piro-api`); adjust domain names as necessary:

            ```bash
            server{
                server_name <your domain name>;

                listen 8082 ssl;

                ssl_certificate /etc/ssl/certs/<your cert>;
                ssl_certificate_key /etc/ssl/certs/<your private key>;

                ssl_session_cache  builtin:1000  shared:SSL:10m;
                ssl_protocols  TLSv1.3;
                ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
                ssl_prefer_server_ciphers on;

                add_header Strict-Transport-Security "max-age=1209600" always;  # 2 weeks
                add_header Content-Security-Policy
                        "default-src 'self' <your domain name>:* *.<your domain name>:*
                        https://cdn.jsdelivr.net
                        https://fastapi.tiangolo.com;
                        script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
                        img-src * data:
                        frame-ancestors 'none'";
                add_header X-Frame-Options SAMEORIGIN always;
                add_header X-Content-Type-Options nosniff;

                location / {
                    include proxy_params;
                    proxy_pass http://127.0.0.1:8000;
                }
            }
            ```

        * Create a new file named 'solr' containing the following (e.g.: `sudo nano solr`); adjust server and ssl cert file names as needed:

            ```bash
            server {
                server_name <your domain name>;

                listen 8989 ssl;

                ssl_certificate /etc/ssl/certs/<your cert>;
                ssl_certificate_key /etc/ssl/certs/<your private key>;

                ssl_session_cache  builtin:1000  shared:SSL:10m;
                ssl_protocols  TLSv1.3;
                ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
                ssl_prefer_server_ciphers on;

                location / {
                    include proxy_params;
                    proxy_pass http://127.0.0.1:8983;
                }
            }
            ```

        * Create a new file named 'solr2' containing the following (e.g.: `sudo nano solr2`); adjust server and ssl cert file names as needed:

            ```bash
            server {
                server_name <your domain name>;

                listen 8990 ssl;

                ssl_certificate /etc/ssl/certs/<your cert>;
                ssl_certificate_key /etc/ssl/certs/<your private key>;

                ssl_session_cache  builtin:1000  shared:SSL:10m;
                ssl_protocols  TLSv1.3;
                ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
                ssl_prefer_server_ciphers on;

                location / {
                    include proxy_params;
                    proxy_pass http://127.0.0.1:8984;
                }
            }
            ```

    * Create new symlinks for the `piro-api` and `piro-ui` apps in the `sites-enabled` directory:

         ```bash
        cd /etc/nginx/sites-enabled
        sudo ln -s /etc/nginx/sites-available/piro-api /etc/nginx/sites-enabled/
        sudo ln -s /etc/nginx/sites-available/piro-ui /etc/nginx/sites-enabled/
        sudo ln -s /etc/nginx/sites-available/solr /etc/nginx/sites-enabled/
        sudo ln -s /etc/nginx/sites-available/solr2 /etc/nginx/sites-enabled/
        ```

    * Test & restart Nginx

        ```bash
        sudo nginx -t
        sudo systemctl restart nginx
        ```

        * You can then test the Nginx reverse proxy by starting up the app under gunicorn (`gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --error-logfile /var/log/gunicorn/error.log --bind 0.0.0.0:8000`), and visiting the website on port 80.
8. Configure gunicorn as a service
    * Navigate to the `/etc/systemd/system` directory and create a file called `piro-api.service`, and update it's contents to match the following:

        ```bash
        [Unit]
        Description=Gunicorn instance to serve the piro-api application
        After=network.target

        [Service]
        User=piro-user
        Group=piro-user
        UMask=017
        WorkingDirectory=/opt/piro-api/piro-api/backend
        Environment="PATH=/opt/piro-api/piro-api_venv/bin"
        ExecStart=/opt/piro-api/piro-api_venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log main:app

        [Install]
        WantedBy=multi-user.target
        ```

    * Enable the piro-api service:

        ```bash
        sudo systemctl enable piro-api
        ```

    * And start the piro-api service:

        ```bash
        sudo systemctl start piro-api
        ```

    * You can then check the status of the piro-api service with `sudo systemctl status piro-api`
9. Configure gunicorn/piro-api Logs
    * Create the directory for log files and set up proper permissions:

        ```bash
        sudo mkdir /var/log/gunicorn
        sudo chown piro-api /var/log/gunicorn
        ```

    * To avoid problems caused by running out of disk space due to logs, we need to configure the logs to be rotated.
        * Create the file `/etc/logrotate.d/gunicorn` containing the following:

            ```bash
            compress

            /var/log/gunicorn/* {
                rotate 10
                daily
            }
            ```

        * Execute the following to turn on the log rotation: `sudo logrotate /etc/logrotate.d/gunicorn`
        * Restart the piro-api service: `sudo systemctl restart piro-api`
