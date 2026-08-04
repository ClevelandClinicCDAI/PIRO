# PIRO: A web-based search platform for pathology reports, leveraging large language models to generate discrete searchable insights

[Journal Link](https://www.sciencedirect.com/science/article/pii/S2153353925000215)

This page documents the technologies and applications used to build PIRO, including the web application that provides the user interface, and various back-end ETL and database/full-text search tools.

## Angular Website User Interface

This is an Angular javascript framework application that provides the user interface to PIRO, serving up content in the form of a 'single page application' (SPA).  It retrieves data from the Python/FastAPI REST API.

The files for this application are served up by Nginx on the webserver.  The files are located in the `/opt/piro-ui` directory on the server.

## Python/FastAPI Application

This application is a RESTful API serving up content from the MS SQL Server Database and SOLR to the Angular application.  Its responsibilities include user authentication and authorization checks, data validation (no validation is performed in the Angular Web Interface), creation/retrieval/updating/deleting of user-specific profile information, and it acts as an interface to the Solr instance.

NGINX is used as a reverse proxy, enforcing HTTPS for all web requests. It proxies to a gunicorn instance, which in turn proxies to the uvicorn workers used by FastAPI.

At launch this application is using LDAP authentication.  But the plan is to, eventually, switch to SSO authentication for a better user experience.

## MS SQL Server Database

The Microsoft SQL Server database is the primary repository of PIRO data.  While most searching occurs against SOLR, the application also utilizes this database for storing/retrieving some PIRO data.  Uses for the data from this database include: user profile information and application configuration information, among other things.  We also stage data in this database before loading it into Solr.

## Solr

PIRO utilizes an Apache Solr instance.  Solr provides the main search feature that is the core of PIRO.

This instance of Solr resides on the PIRO web server.  PIRO data is loaded into Solr on a regular basis - via Airflow - to facilitate the search features in the PIRO interface.

## SSIS

Additionally, we use Microsoft's SSIS software to load data into PIRO from the Clarity database.  The code for these load jobs resides on the database server itself, and is executed from those servers (Note: this is a different server than our primary DB server - one specifically for SSIS).

The SSIS jobs are triggered via our Airflow server (DAG names: 'ssis_delta_load_job' & 'ssis_full_load_job').  The Airflow servers execute a stored procedure to fire off the jobs on the SSIS server.

## Airflow

We use an instance of the Apache Airflow application as a job scheduling tool for PIRO.  It is used primarily to load data: from the Clarity database into PIRO's SQL Server instance, and from PIRO's SQL Server instance into Solr, along with other duties.

## Docker Compose Quickstart

You can run the complete PIRO stack locally (SQL Server, Solr, FastAPI, and the Angular UI) with Docker Compose. Everything lives at the repository root now: the Compose file is `docker-compose.yml`, the sample-data container is built from `./piro-sample-data`, Solr builds from `./piro-solr`, and the UI reverse proxy ships with `./piro-ui/nginx.conf`.

### Repository layout for Compose assets

- `docker-compose.yml` – defines the five core services (SQL Server, Solr, sample-data bootstrapper, FastAPI, Angular UI).
- `piro-sample-data/` – Dockerfile, entrypoint script, SQL/Solr fixtures, and helpers (pulls schema scripts from `piro-sql/`).
- `piro-solr/` – Solr Dockerfile, `create-cores.sh`, and versioned config sets under `V8/` and `V9/`.
- `piro-ui/nginx.conf` – the nginx site definition used by the UI container to proxy `/api` to FastAPI.

### Prerequisites

- Docker Desktop **or** the Docker Engine CLI plus the Compose plugin (`docker compose`).
- ~8 GB of free RAM (SQL Server + Solr are memory hungry).

### Quick copy/paste setup (recommended first run)

Windows (PowerShell):

```powershell
Copy-Item .env.template .env
Copy-Item piro-ui\src\assets\config.example.json piro-ui\src\assets\config.json
docker compose up --build
```

macOS / Linux:

```bash
cp .env.template .env
cp piro-ui/src/assets/config.example.json piro-ui/src/assets/config.json
docker compose up --build
```

If you need OAuth group-based login locally, set both `MOCK_OAUTH_AD_GROUP` and `OIDC_ALLOWED_GROUPS` to the same group value in `.env`.

### UI configuration file

Before building the `ui` image you must create `piro-ui/src/assets/config.json`. The Angular app fetches this file at runtime to discover the API base URL and other environment-specific values, and the UI Dockerfile bakes it into the compiled bundle via `COPY piro-ui/ .` — if the file is missing, the built image will 404 on `assets/config.json` and the UI will fail to load.

A template lives at `piro-ui/src/assets/config.example.json`. Copy it and edit the values:

macOS / Linux:

```bash
cp piro-ui/src/assets/config.example.json piro-ui/src/assets/config.json
```

Windows (PowerShell):

```powershell
Copy-Item piro-ui\src\assets\config.example.json piro-ui\src\assets\config.json
```

Then open `piro-ui/src/assets/config.json` and set:

- `apiBaseUrl` – URL the browser uses to reach the FastAPI backend. For the local Compose stack use `/api/` (nginx in the `ui` container proxies `/api/` to the `api` service). For a direct-to-API setup use `http://localhost:8001/`.
- `irbDisclaimerText` – the disclaimer string shown in the UI. Substitute your institution's wording.

> **Note:** `piro-ui/src/assets/config.json` is gitignored (`piro-ui/.gitignore`) so environment-specific values never end up in version control. Recreate the file on every clean checkout, and rebuild the `ui` image (`docker compose build ui`) after any change to it.

### Local OAuth/SSO testing

#### `hosts` file entry

The Compose stack includes a `mock-oauth` service (based on `ghcr.io/navikt/mock-oauth2-server`) that stands in for the organization's SSO provider so you can exercise the OAuth login flow entirely on your workstation, with no VPN or corporate network access required.

For this to work, the mock IdP must be reachable at the **same hostname** from both your browser (during the redirect to the login page) and the `api` container (during token exchange and JWKS lookup). Otherwise the `iss` claim on the issued JWT will not match what the API expects and token validation will fail.

The Compose file uses `piro-auth` as that shared hostname. You must map it to `127.0.0.1` in your OS `hosts` file **before** running `docker compose up`:

- **Windows:** open `C:\Windows\System32\drivers\etc\hosts` in an editor running as Administrator and add:

    ```text
    127.0.0.1  piro-auth
    ```

- **macOS / Linux:** append the same line to `/etc/hosts` (needs `sudo`):

    ```bash
    echo "127.0.0.1  piro-auth" | sudo tee -a /etc/hosts
    ```

Inside the `api` container the same name resolves via the `extra_hosts: - "piro-auth:host-gateway"` entry already defined in `docker-compose.yml`, so no additional configuration is needed there.

Once the entry is in place, the mock login page is reachable at <http://piro-auth:8888/piro> and the UI's OAuth redirect flow will complete against it. To skip OAuth entirely and use the legacy LDAP bypass instead, set `ACCESS_TOKEN_TEST_USER` as described below.

#### OAuth AD Group

Docker Compose evaluates `${...}` variables at compose-time from your shell environment and the repo-root `.env` file. To keep local setup in one place, use `.env` for all localhost overrides:

```powershell
Copy-Item .env.template .env
```

Then edit `.env` with your local values. The repository no longer relies on `docker-compose.override.yml` for local auth/database overrides.

Important `.env` notes:

- `MOCK_OAUTH_AD_GROUP` controls the `groups` claim emitted by `mock-oauth`.
- `OIDC_ALLOWED_GROUPS` controls the API authorization allow-list.
- These two values must overlap (typically identical) or OAuth login will fail with a group mismatch.
- If you are using the full local stack (`sqlserver` and `solr` containers), keep:
  - `MSSQL_SERVER=sqlserver`
  - `SOLR_URL=http://solr:8983/solr`
  - `MSSQL_USER=sa`
  and set `PIRO_MSSQL_SA_PASSWORD` to match the SQL Server password used by Compose.
- `.env` is gitignored; do not commit local secrets or environment-specific credentials.

### One-time bootstrap with sample data

macOS / Linux:

```bash
# from the repo root
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_MSSQL_SA_PASSWORD='ChooseA$trongPassword' \
docker compose up --build
```

Windows (PowerShell):

```powershell
# from the repo root
$env:PIRO_LOAD_SAMPLE_DATA="true"
$env:PIRO_MSSQL_SA_PASSWORD="ChooseA`$trongPassword"
docker compose up --build
```

Behind the scenes:

- `sqlserver` (official SQL Server 2022 image) exposes `localhost:1433` and persists data in the `sql_data` Docker volume.
- `solr` builds from `piro-solr/Dockerfile`, copies the checked-in config sets, runs `create-cores.sh`, and listens on `http://localhost:8983`.
- `sample-data` builds from `piro-sample-data/Dockerfile`, waits for SQL + Solr, redeploys every schema from `piro-sql`, and optionally loads curated demo data into both systems when `PIRO_LOAD_SAMPLE_DATA=true`.
- `api` builds from `./piro-api` with ODBC Driver 18, exposes Swagger UI on `http://localhost:8001/docs`, and expects Solr + SQL hostnames from Compose networking.
- `ui` builds `./piro-ui`, copies the compiled Angular build artifacts plus `nginx.conf`, and serves the SPA via `http://localhost:8080` (proxying `/api` to `api`).

### Useful configuration knobs

- `PIRO_ACCESS_TOKEN_SECRET` – JWT signing secret for FastAPI (defaults to `change-me`).
- `PIRO_MSSQL_SA_PASSWORD` – SQL `sa` password used by SQL Server and every dependent container (defaults to `P1ro!LocalDev`).
- `PIRO_BOOTSTRAP_DB` – `false` keeps existing MDF/LDF files and skips schema reapply on the next `docker compose up`.
- `PIRO_FORCE_RESET` – `true` drops/recreates the PIRO database before schema deployment (defaults to `true`).
- `PIRO_LOAD_SAMPLE_DATA` – `true` re-imports demo SQL + Solr docs, `false` leaves the schema empty.
- `PIRO_SAMPLE_USER_*` – seeds a specific account into SQL + Solr for local testing (`NUID`, `FIRST_NAME`, `LAST_NAME`, `ROLE`).
- `AD_LDAP_PATH`, `AD_SECURITY_GROUP`, `AD_DOMAIN` – plug real directory settings in when you want LDAP-backed auth inside the API container.
- `ACCESS_TOKEN_TEST_USER` – comma-separated usernames allowed to bypass LDAP when running locally (unset by default; set explicitly, e.g., `ACCESS_TOKEN_TEST_USER=demo.user`, only when you need the bypass).
- `AIRFLOW_DAG_COHORT_LOADER_URL` – full URL of the Airflow DAG-run endpoint the API posts to when a user creates a cohort (e.g. `https://<airflow-host>/api/v2/dags/solr_cohort_load/dagRuns`). Required for cohort creation.
- `AIRFLOW_USERNAME`, `AIRFLOW_PASSWORD` – credentials the API uses to obtain a JWT bearer token from the Airflow auth endpoint before triggering the DAG. Required for cohort creation.
- `AIRFLOW_CERTIFICATE` – filename (not path) of the PEM file used to verify TLS against the Airflow host, e.g. `[certificate_name].pem`. The file must exist inside the API image at `/app/certificates/<filename>` (source: `piro-api/backend/certificates/`). Required for cohort creation.

### Enabling cohort creation (Airflow integration)

The API's `POST /cohort/create` endpoint triggers an Airflow DAG that loads the new cohort into Solr. Two things must be in place:

1. **Certificate file on disk.** Place the PEM used to verify TLS to your Airflow host in `piro-api/backend/certificates/` (see [Providing certificate files](#providing-certificate-files) below for how to obtain and copy the file). Files there are gitignored (`piro-api/.gitignore` ignores `*.pem`) but are still baked into the API image at build time via `COPY backend /app` — Docker builds do not honor `.gitignore`. Rebuild the API image (`docker compose build api`) after adding or replacing a cert.
2. **Environment variables.** Set the four `AIRFLOW_*` variables listed above. If any of them are unset or empty, the API returns HTTP 500 with `FileNotFoundError: Certificates directory not found` — the message is misleading; the same error covers a missing cert *and* a missing `AIRFLOW_CERTIFICATE` value.

#### Providing certificate files

The `piro-api/backend/certificates/` directory is where the API expects to find any PEM files it needs to verify TLS connections to external services (currently just the Airflow host used by cohort creation). The directory itself is checked in but its `*.pem` contents are gitignored, so you must supply the file yourself before building the API image.

Steps:

1. **Obtain the PEM.** Ask an administrator for the certificate that matches the Airflow host you plan to talk to. If you already have the host's cert in another format, convert it to PEM (`openssl x509 -in cert.crt -out cert.pem -outform PEM`).
2. **Copy it into the repo.** Drop the file into `piro-api/backend/certificates/`. The filename you use here is what you'll set `AIRFLOW_CERTIFICATE` to — no path, just the filename.
3. **Rebuild the API image** so the new file is baked into `/app/certificates/` inside the container:

    ```bash
    docker compose build api
    ```

> **Note:** Never commit `*.pem` files to git. The `.gitignore` entry at `piro-api/.gitignore` (`*.pem`) already blocks them, but double-check `git status` before committing after touching this directory.

Example (macOS / Linux):

```bash
AIRFLOW_CERTIFICATE=<certificate_file_name> \
AIRFLOW_DAG_COHORT_LOADER_URL="https://<airflow-host>/api/v2/dags/solr_cohort_load/dagRuns" \
AIRFLOW_USERNAME=<user> \
AIRFLOW_PASSWORD=<password> \
docker compose up --no-deps api ui
```

Example (Windows PowerShell):

```powershell
$env:AIRFLOW_CERTIFICATE="<certificate_file_name>"
$env:AIRFLOW_DAG_COHORT_LOADER_URL="https://<airflow-host>/api/v2/dags/solr_cohort_load/dagRuns"
$env:AIRFLOW_USERNAME="<user>"
$env:AIRFLOW_PASSWORD="<password>"
docker compose up --no-deps api ui
```

Only env changed? No rebuild needed — `docker compose up` picks up new values on container recreate.

Default demo login: set `ACCESS_TOKEN_TEST_USER=demo.user` in your shell or `.env` file before running `docker compose up`, then sign in via the UI as `demo.user` with any password. Leave this variable unset in shared or production-like environments to avoid enabling the bypass.

### Common Docker Compose launch recipes

Replace placeholder values (`ChooseA$trongPassword`, `ldap.example.org`, `CN=Your-Security-Group,...`, etc.) with settings from your own environment before running the commands.

**Offline demo (no LDAP required)** – loads curated data and enables the `demo.user` bypass account:

macOS / Linux:

```bash
ACCESS_TOKEN_TEST_USER=demo.user \
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_SAMPLE_USER_NUID=demo.user \
PIRO_SAMPLE_USER_FIRST_NAME=Demo \
PIRO_SAMPLE_USER_LAST_NAME=User \
PIRO_SAMPLE_USER_ROLE=USER \
docker compose up --build
```

Windows (PowerShell):

```powershell
$env:ACCESS_TOKEN_TEST_USER="demo.user"
$env:PIRO_LOAD_SAMPLE_DATA="true"
$env:PIRO_SAMPLE_USER_NUID="demo.user"
$env:PIRO_SAMPLE_USER_FIRST_NAME="Demo"
$env:PIRO_SAMPLE_USER_LAST_NAME="User"
$env:PIRO_SAMPLE_USER_ROLE="USER"
docker compose up --build
```

**First-time LDAP initialization with sample data** – run while connected to your corporate network so LDAP lookups succeed:

macOS / Linux:

```bash
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_SAMPLE_USER_NUID=your.user@your-domain.org \
PIRO_SAMPLE_USER_FIRST_NAME=YourName \
PIRO_SAMPLE_USER_LAST_NAME=YourLast \
PIRO_SAMPLE_USER_ROLE=USER \
AD_LDAP_PATH="ldaps://ldap.example.org:3269" \
AD_SECURITY_GROUP="CN=PIRO-Dev,OU=Groups,DC=example,DC=org" \
AD_DOMAIN=example.org \
docker compose up --build
```

Windows (PowerShell):

```powershell
$env:PIRO_LOAD_SAMPLE_DATA="true"
$env:PIRO_SAMPLE_USER_NUID="your.user@your-domain.org"
$env:PIRO_SAMPLE_USER_FIRST_NAME="YourName"
$env:PIRO_SAMPLE_USER_LAST_NAME="YourLast"
$env:PIRO_SAMPLE_USER_ROLE="USER"
$env:AD_LDAP_PATH="ldaps://ldap.example.org:3269"
$env:AD_SECURITY_GROUP="CN=PIRO-Dev,OU=Groups,DC=example,DC=org"
$env:AD_DOMAIN="example.org"
docker compose up --build
```

**Production-like run (LDAP only, no sample data)** – skip demo content once you have real data restored locally:

macOS / Linux:

```bash
PIRO_LOAD_SAMPLE_DATA=false \
AD_LDAP_PATH="ldaps://ldap.example.org:3269" \
AD_SECURITY_GROUP="CN=PIRO-Prod,OU=Groups,DC=example,DC=org" \
AD_DOMAIN=example.org \
docker compose up --build
```

Windows (PowerShell):

```powershell
$env:PIRO_LOAD_SAMPLE_DATA="false"
$env:AD_LDAP_PATH="ldaps://ldap.example.org:3269"
$env:AD_SECURITY_GROUP="CN=PIRO-Prod,OU=Groups,DC=example,DC=org"
$env:AD_DOMAIN="example.org"
docker compose up --build
```

> **Tip (Windows):** `$env:` assignments are session-scoped and will not persist after you close the terminal. To unset a variable after use, run `Remove-Item Env:\VARIABLE_NAME` (e.g. `Remove-Item Env:\ACCESS_TOKEN_TEST_USER`).

### Ports, health, and tear-down

- UI: <http://localhost:8080>
- API (direct): <http://localhost:8001/docs>
- Solr: <http://localhost:8983/solr>
- SQL Server: localhost:1433 (SQL authentication, database `PIRO`).

Press `Ctrl+C` to stop the stack. To remove containers/volumes afterwards:

```bash
docker compose down
# WARNING: The following command will REMOVE all volumes, including the persistent SQL volume!
docker compose down --volumes
# To keep the persistent SQL volume, run `docker compose down` without the `--volumes` flag.
```

If you need to inspect the schema/data bootstrap logs, run:

```bash
docker compose logs sample-data
```
