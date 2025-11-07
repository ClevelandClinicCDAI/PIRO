# PIRO: A web-based search platform for pathology reports, leveraging large language models to generate discrete searchable insights

[Journal Link](https://www.sciencedirect.com/science/article/pii/S2153353925000215)

This page documents the technologies and applications used to build PIRO, including the web application that provides the user interface, and various back-end ETL and database/full-text search tools.

## Angular Website User Interface

This is an Angular javascript framework application that provides the user interface to PIRO, serving up content in the form of a 'single page application' (SPA).  It retrieves data from the Python/FastAPI REST API.

The files for this application are served up by Nginx on the webserver.  The files are located in the `/opt/piro-ui` directory on the server.

## Python/FastAPI Application

This application is a RESTful API serving up content from the MS SQL Server Database and SOLR to the Angular application.  It's responsibilities include user authentication and authorization checks, data validation (no validation is performed in the Angular Web Interface), creation/retrieval/updating/deleting of user-specific profile information, and it acts as an interface to the Solr instance.  

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

### One-time bootstrap with sample data

```bash
# from the repo root
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_MSSQL_SA_PASSWORD='ChooseA$trongPassword' \
docker compose up --build
```

Behind the scenes:

- `sqlserver` (official SQL Server 2022 image) exposes `localhost:1433` and persists data in the `sql_data` Docker volume.
- `solr` builds from `piro-solr/Dockerfile`, copies the checked-in config sets, runs `create-cores.sh`, and listens on `http://localhost:8983`.
- `sample-data` builds from `piro-sample-data/Dockerfile`, waits for SQL + Solr, redeploys every schema from `piro-sql`, and optionally loads curated demo data into both systems when `PIRO_LOAD_SAMPLE_DATA=true`.
- `api` builds from `./piro-api` with ODBC Driver 18, exposes Swagger UI on `http://localhost:8001/docs`, and expects Solr + SQL hostnames from Compose networking.
- `ui` builds `./piro-ui`, copies `ngx` artifacts plus `nginx.conf`, and serves the SPA via `http://localhost:8080` (proxying `/api` to `api`).

### Useful configuration knobs

- `PIRO_ACCESS_TOKEN_SECRET` – JWT signing secret for FastAPI (defaults to `change-me`).
- `PIRO_MSSQL_SA_PASSWORD` – SQL `sa` password used by SQL Server and every dependent container (defaults to `P1ro!LocalDev`).
- `PIRO_BOOTSTRAP_DB` – `false` keeps existing MDF/LDF files and skips schema reapply on the next `docker compose up`.
- `PIRO_FORCE_RESET` – `true` drops/recreates the PIRO database before schema deployment (defaults to `true`).
- `PIRO_LOAD_SAMPLE_DATA` – `true` re-imports demo SQL + Solr docs, `false` leaves the schema empty.
- `PIRO_SAMPLE_USER_*` – seeds a specific account into SQL + Solr for local testing (`NUID`, `FIRST_NAME`, `LAST_NAME`, `ROLE`).
- `AD_LDAP_PATH`, `AD_SECURITY_GROUP`, `AD_DOMAIN` – plug real directory settings in when you want LDAP-backed auth inside the API container.
- `ACCESS_TOKEN_TEST_USER` – comma-separated usernames allowed to bypass LDAP when running locally (default `demo.user`).

Default demo login: set `ACCESS_TOKEN_TEST_USER=demo.user` (already done in `docker-compose.yml`), then sign in via the UI as `demo.user` with any password.

### Common Docker Compose launch recipes

Replace placeholder values (`ChooseA$trongPassword`, `ldap.example.org`, `CN=Your-Security-Group,...`, etc.) with settings from your own environment before running the commands.

**Offline demo (no LDAP required)** – loads curated data and enables the `demo.user` bypass account:

```bash
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_SAMPLE_USER_NUID=demo.user \
PIRO_SAMPLE_USER_FIRST_NAME=Demo \
PIRO_SAMPLE_USER_LAST_NAME=User \
PIRO_SAMPLE_USER_ROLE=USER \
docker compose up --build
```

**First-time LDAP initialization with sample data** – run while connected to your corporate network so LDAP lookups succeed:

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

**Production-like run (LDAP only, no sample data)** – skip demo content once you have real data restored locally:

```bash
PIRO_LOAD_SAMPLE_DATA=false \
AD_LDAP_PATH="ldaps://ldap.example.org:3269" \
AD_SECURITY_GROUP="CN=PIRO-Prod,OU=Groups,DC=example,DC=org" \
AD_DOMAIN=example.org \
docker compose up --build
```

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
