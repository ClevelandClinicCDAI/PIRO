This page documents the technologies and applications used to build PIRO, including the web application that provides the user interface, and various back-end ETL and database/full-text search tools.

# Angular Website User Interface
This is an Angular javascript framework application that provides the user interface to PIRO, serving up content in the form of a 'single page application' (SPA).  It retrieves data from the Python/FastAPI REST API.

The files for this application are served up by Nginx on the webserver.  The files are located in the `/opt/piro-ui` directory on the server.

# Python/FastAPI Application
This application is a RESTful API serving up content from the MS SQL Server Database and SOLR to the Angular application.  It's responsibilities include user authentication and authorization checks, data validation (no validation is performed in the Angular Web Interface), creation/retrieval/updating/deleting of user-specific profile information, and it acts as an interface to the Solr instance.  

NGINX is used as a reverse proxy, enforcing HTTPS for all web requests. It proxies to a gunicorn instance, which in turn proxies to the uvicorn workers used by FastAPI.

At launch this application is using LDAP authentication.  But the plan is to, eventually, switch to SSO authentication for a better user experience.

# MS SQL Server Database
The Microsoft SQL Server database is the primary repository of PIRO data.  While most searching occurs against SOLR, the application also utilizes this database for storing/retrieving some PIRO data.  Uses for the data from this database include: user profile information and application configuration information, among other things.  We also stage data in this database before loading it into Solr.

# Solr
PIRO utilizes an Apache Solr instance.  Solr provides the main search feature that is the core of PIRO.

This instance of Solr resides on the PIRO web server.  PIRO data is loaded into Solr on a regular basis - via Airflow - to facilitate the search features in the PIRO interface.

## SSIS
Additionally, we use Microsoft's SSIS software to load data into PIRO from the Clarity database.  The code for these load jobs resides on the database server itself, and is executed from those servers (Note: this is a different server than our primary DB server - one specifically for SSIS).

The SSIS jobs are triggered via our Airflow server (DAG names: 'ssis_delta_load_job' & 'ssis_full_load_job').  The Airflow servers execute a stored procedure to fire off the jobs on the SSIS server.

# Airflow
We use an instance of the Apache Airflow application as a job scheduling tool for PIRO.  It is used primarily to load data: from the Clarity database into PIRO's SQL Server instance, and from PIRO's SQL Server instance into Solr, along with other duties.

## Docker Compose Quickstart

You can run the complete PIRO stack locally (SQL Server, Solr, FastAPI, and the Angular UI) with Docker Compose. The new workflow lives at the repository root and relies on the files in `docker-compose.yml` plus the helper assets inside the `docker/` directory.

### Prerequisites

- Docker Desktop **or** the Docker Engine CLI plus the Compose plugin (`docker compose` command).
- ~8 GB of free RAM (SQL Server + Solr are memory hungry).

### One-time bootstrap with sample data

```bash
# from the repo root
PIRO_LOAD_SAMPLE_DATA=true \
PIRO_MSSQL_SA_PASSWORD='ChooseA$trongPassword' \
docker compose up --build
```

What happens:

- `sqlserver` starts Microsoft SQL Server 2022 and listens on `localhost:1433`.
- `solr` builds from the checked-in PIRO config sets and exposes the admin UI on `http://localhost:8983`.
- `sample-data` waits for both services, deploys every schema script from `piro-sql`, and (optionally) loads the curated demo dataset into SQL Server and Solr when `PIRO_LOAD_SAMPLE_DATA=true`.
- `api` builds the FastAPI service with ODBC Driver 18 and exposes it on `http://localhost:8001` (the UI proxies to it via `/api`).
- `ui` builds the Angular application and serves it via nginx on `http://localhost:8080`.

Default login for the demo data is `demo.user` with any password (the API trusts usernames listed in `ACCESS_TOKEN_TEST_USER` for local use). You can change the hard-coded secrets by setting:

- `PIRO_ACCESS_TOKEN_SECRET` – JWT signing secret (defaults to `change-me`).
- `PIRO_MSSQL_SA_PASSWORD` – SQL Server `sa` password (defaults to `P1ro!LocalDev`).
- `PIRO_BOOTSTRAP_DB` – set to `false` to keep the existing database files and skip schema re-deployment on the next `docker compose up`.
- `PIRO_FORCE_RESET` – when `true`, forces the database to be dropped/recreated before schema files run (defaults to `true`).
- `PIRO_LOAD_SAMPLE_DATA` – set to `true` to re-import the curated demo data set, `false` to start with empty tables.

Ports and URLs:

- UI: <http://localhost:8080>
- API (direct): <http://localhost:8001/docs>
- Solr: <http://localhost:8983/solr>
- SQL Server: localhost:1433 (SQL authentication, database `PIRO`).

To stop the stack press `Ctrl+C`. To remove containers/volumes afterwards:

```bash
docker compose down
# or keep the persistent SQL volume
docker compose down --volumes
```

If you need to inspect the schema/data bootstrap logs, run `docker compose logs sample-data`.
