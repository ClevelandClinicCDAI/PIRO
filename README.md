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

You can now run the **entire PIRO stack** locally – FastAPI, Angular UI, Solr (V9 configs), optional local SQL Server + sample data, **plus a full Airflow instance** that drives Solr indexing using the repository’s DAGs. Everything lives at the repository root: `docker-compose.yml` orchestrates it all.

### Repository layout for Compose assets

- `docker-compose.yml` – defines Solr, FastAPI, Angular UI, Airflow + Postgres metadata DB, and opt-in SQL Server + sample-data bootstrapper (via profiles).
- `piro-airflow/` – DAGs and task code used by the stack’s Airflow container.
- `piro-sample-data/` – Dockerfile, entrypoint script, SQL fixtures, and helpers (pulls schema scripts from `piro-sql/`).
- `piro-solr/` – Solr Dockerfile, `create-cores.sh`, and versioned config sets under `V8/` and `V9/` (Compose builds V9 by default).
- `piro-ui/nginx.conf` – nginx site definition used by the UI container to proxy `/api` to FastAPI.

### Prerequisites

- Docker Desktop **or** the Docker Engine CLI plus the Compose plugin (`docker compose`).
- ~8 GB of free RAM (SQL Server + Solr are memory hungry).

### Profiles and what they do

- Default (no profile): starts Solr, Airflow (+ Postgres metadata DB), API, UI. Expects you to point at an **external SQL Server** via env vars.
- `local-mssql` profile: adds the local `sqlserver` container **and** the `sample-data` bootstrapper so you can bring your own database if you want everything self-contained.

### One-time bootstrap with local SQL + sample data

```bash
# from the repo root
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_MSSQL_SA_PASSWORD='ChooseA$trongPassword' \
docker compose --profile local-mssql up --build
```

Behind the scenes (with `local-mssql`):

- `sqlserver` (official SQL Server 2022 image) exposes `localhost:1433` and persists data in the `sql_data` Docker volume.
- `sample-data` waits for SQL + Solr, deploys schemas from `piro-sql`, and only loads demo content when `PIRO_LOAD_SAMPLE_DATA=true`.
- `solr` builds V9 cores and stores indexes in the named volume `solr_data` so restarts are fast.
- `airflow-db` (Postgres) and `airflow` (Apache Airflow 2.8) run continuously; Airflow gets DAGs from `./piro-airflow` and uses env-injected Variables for SQL and Solr connection info.
- `api` exposes Swagger UI on `http://localhost:8001/docs` and talks to the SQL/Solr hosts you provide.
- `ui` serves the SPA on `http://localhost:8080`.

### Useful configuration knobs

- **SQL targeting** (works for both API and Airflow):
  - `PIRO_MSSQL_HOST`, `PIRO_MSSQL_PORT` (default `1433`), `PIRO_MSSQL_INSTANCE` (optional), `PIRO_MSSQL_USERNAME`, `PIRO_MSSQL_SA_PASSWORD`, `PIRO_MSSQL_DB`.
  - Add `--profile local-mssql` if you want the bundled SQL + sample-data instead of an external instance.
- **Sample data/bootstrap**: `PIRO_BOOTSTRAP_DB` (default `true`), `PIRO_FORCE_RESET` (default `true`), `PIRO_LOAD_SAMPLE_DATA` (default `false`), `PIRO_SAMPLE_USER_*` for demo user seeding.
- **Solr**: persists to `solr_data` volume; no DIH in V9—indexing is handled by the Airflow DAGs included in this repo.
- **Airflow**: web UI on `http://localhost:8084` (admin/admin by default). Variables are fed from env (`AIRFLOW_VAR_*`) and already mapped from the `PIRO_*` settings above. If you point the stack at remote SQL/Solr, just set the corresponding `PIRO_*` envs before `docker compose up`.
- **Auth + UI**: `PIRO_ACCESS_TOKEN_SECRET`, `ACCESS_TOKEN_TEST_USER` (local bypass), LDAP settings (`AD_LDAP_PATH`, `AD_SECURITY_GROUP`, `AD_DOMAIN`).

Default demo login: set `ACCESS_TOKEN_TEST_USER=demo.user` in your shell or `.env` file before running `docker compose up`, then sign in via the UI as `demo.user` with any password. Leave this variable unset in shared or production-like environments to avoid enabling the bypass.

### Common Docker Compose launch recipes

Replace placeholder values (`ChooseA$trongPassword`, `ldap.example.org`, `CN=Your-Security-Group,...`, etc.) with settings from your own environment before running the commands.

**Offline demo (no LDAP required)** – runs local SQL + sample data + Airflow + Solr:

```bash
ACCESS_TOKEN_TEST_USER=demo.user \
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_SAMPLE_USER_NUID=demo.user \
PIRO_SAMPLE_USER_FIRST_NAME=Demo \
PIRO_SAMPLE_USER_LAST_NAME=User \
PIRO_SAMPLE_USER_ROLE=USER \
docker compose --profile local-mssql up --build
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

**Production-like run (LDAP only, no sample data; external SQL/Solr)** – point API+Airflow at your real hosts, skip local SQL and sample-data:

```bash
PIRO_MSSQL_HOST=your-sql-host \
PIRO_MSSQL_INSTANCE=YOURINSTANCE \
PIRO_MSSQL_USERNAME=piro_etl \
PIRO_MSSQL_SA_PASSWORD='strong' \
PIRO_MSSQL_DB=PIRO \
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
- Airflow UI: <http://localhost:8084>
- SQL Server (when `local-mssql` profile enabled): localhost:1433 (database `PIRO`).

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
