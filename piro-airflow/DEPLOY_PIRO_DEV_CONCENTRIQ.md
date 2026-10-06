# PIRO-DEV: Deploy the Concentriq PostgreSQL catalog integration

The integration reads cases with ready whole-slide images from Concentriq's PostgreSQL database, matches them to PIRO by accession number, and updates the existing image filter and viewer links. Each refresh reconciles the full catalog, including images added to older cases and cases whose images are no longer available.

## 1. Prepare the deployment

- [ ] Use the deployment revision from branch `feature/concentriq-postgres-sync`, including the new files listed below.
- [ ] Confirm all targets are DEV:

| Component | Target |
|---|---|
| PIRO SQL Server | `10.88.62.23,52793`, database `PIRO_DEV` |
| Concentriq PostgreSQL source | `10.88.45.73:5432`, database `dx` |
| Solr | `https://dev-piro.ccf.org:8989/solr`, core `PIROCase` |
| Airflow | Existing PIRO-DEV Airflow server |

- [ ] Retrieve PostgreSQL credentials from the supplied local override or the team's secret store. Keep credentials out of the deployment commit.
- [ ] Keep `concentriq_load` paused until the database changes and Airflow configuration are ready.

## 2. Deploy SQL objects to PIRO_DEV

- [ ] Apply these scripts in order. Paths are relative to the repository root.

| Order | Script | Change |
|---|---|---|
| 1 | `piro-sql/Table/dbo.ConcentriqCase.Table.sql` | Retain the existing table and add the `CaseNumber` matching index |
| 2 | `piro-sql/Table/dbo.ConcentriqConfig.Table.sql` | Create the configuration table only if absent |
| 3 | `piro-sql/Airflow/PROCS/dbo.P_AIRFLOW_Concentriq_Case_Load.StoredProcedure.sql` | Update case associations, image flags, and Solr delta records |
| 4 | `piro-sql/Airflow/PROCS/dbo.P_AIRFLOW_Concentriq_Case_Delete.StoredProcedure.sql` | Update reset behavior |
| 5 | `piro-sql/Airflow/PROCS/dbo.P_AIRFLOW_Concentriq_Case_Sync.StoredProcedure.sql` | Add transactional catalog synchronization |
| 6 | `piro-sql/SSIS/PROCS/LOADER-SOLR/dbo.P_SSIS_LoadCaseSolr.StoredProcedure.sql` | Ensure subsequent SSIS loads respect inactive catalog records |

- [ ] Confirm the Airflow SQL account can execute the procedures, read the configuration, and perform the table operations required by the dynamic SQL that populates `CaseSolr_Delta`.
- [ ] Create or update one active row in `dbo.ConcentriqConfig` with `[Key]='CaseDetails.Get.Enabled'`, `[Value]='true'`, and `IsActive=1`.

No new columns are required in the existing PIRO-DEV tables. Staging uses temporary tables. No PostgreSQL schema changes are required.

## 3. Deploy Airflow code

- [ ] Confirm the DEV DAG directory:

```bash
/opt/piro-airflow/piro-airflow_venv/bin/airflow config get-value core dags_folder
```

The documented destination is `/opt/piro-airflow/piro-airflow/`. Deploy the following files from `piro-airflow/`, preserving their relative paths:

```text
piro_dags.py
tasks/concentriq_case_load_task.py
tasks/loaders/concentriq_catalog.py
tasks/loaders/concentriq_case_loader.py
tasks/loaders/solr_case_data_loader.py
tasks/utils/concentriq_setup.py
```

- [ ] Confirm the Airflow virtual environment includes the existing SQLAlchemy and pymssql dependencies plus `psycopg2-binary`, as specified in `piro-airflow/requirements.txt`.
- [ ] Confirm the DAG processor picks up the deployment and reports no import errors.
- [ ] Run the focused tests using a test environment with pytest installed:

```bash
cd piro-airflow
python -m pytest tests -q
```

## 4. Configure DEV Airflow Variables

- [ ] Set the following Airflow Variables, or their `AIRFLOW_VAR_` environment equivalents:

| Variable | Value |
|---|---|
| `CONCENTRIQ_DB_SERVER` | `10.88.45.73` |
| `CONCENTRIQ_DB_PORT` | `5432` |
| `CONCENTRIQ_DB_NAME` | `dx` |
| `CONCENTRIQ_DB_USER` | Supplied PostgreSQL username |
| `CONCENTRIQ_DB_PASSWORD` | Supplied PostgreSQL password |
| `CONCENTRIQ_DB_SSLMODE` | `prefer` — the inspected server does not support SSL |
| `CONCENTRIQ_CASE_DETAIL_PAGE_SIZE` | `1000` |
| `CONCENTRIQ_CASE_DB_RELOAD_DATA` | `0` |

- [ ] Confirm the existing `PIRO_DB_*` Variables target `PIRO_DEV` and the existing Solr Variables target the DEV `PIROCase` core.
- [ ] Verify connectivity from the Airflow execution host to both databases and Solr. Verify SELECT access to PostgreSQL `public.case_details`, `public.slides`, and `public.images`.

The workstation's `docker-compose.override.yml` does not configure the Airflow server. The old Concentriq API URL, Basic Auth header, and API certificate settings are no longer used by this loader.

## 5. Configure viewer links and confirm Solr

- [ ] Obtain the Concentriq browser URL prefix for a case, ending immediately before the case ID.
- [ ] Set that prefix as `CONCENTRIQ_URL` in the DEV API environment and restart the API to load it. For Docker deployments, the updated `docker-compose.yml` passes this setting to the API.
- [ ] Confirm the DEV Solr core still contains indexed and stored fields `isconcentriq` (`boolean`) and `concentriqid` (`pint`).

The running DEV server was verified as Solr **9.8.1**, with field definitions matching the checked-in V9 schema. No Solr schema update or full index rebuild is needed. The UI already implements the image filter and viewer links.

## 6. Run the initial backfill

- [ ] Choose a window without another Solr load or SSIS delta refresh modifying the shared staging tables.
- [ ] Manually trigger `concentriq_load` in Airflow. No date parameters or reset are needed.
- [ ] Wait for success and review the staged/synchronized record count. The source contained **85,902 cases with ready images** when inspected; this count can change and is not the number necessarily matched to PIRO.
- [ ] Inspect the PIRO results:

```sql
USE [PIRO_DEV];

SELECT COUNT(*) AS ActiveCatalogCases
FROM dbo.ConcentriqCase WHERE IsActive = 1;

SELECT COUNT(*) AS MatchedCatalogCases
FROM dbo.ConcentriqCase WHERE IsActive = 1 AND CaseId <> -1;

SELECT COUNT(*) AS PiroCasesWithImages
FROM dbo.CaseSolr WHERE IsConcentriq = 1;

SELECT COUNT(*) AS PendingSolrRecords
FROM dbo.CaseSolr_Delta;
```

- [ ] Trigger `solr_case_load` after the catalog refresh succeeds, and wait for success.
- [ ] Verify known matched cases have `isconcentriq=true` and the correct `concentriqid` in Solr. Confirm PIRO's Yes/No filter and Concentriq links work.
- [ ] Re-run `concentriq_load` and confirm it completes without duplicate catalog entries.

## 7. Enable nightly operation

- [ ] Unpause `concentriq_load`. Confirm **12:30 AM Eastern** (`30 0 * * *`), `max_active_runs=1`, and `catchup=False`.
- [ ] Confirm the separate `solr_case_load` DAG remains enabled at **6:00 AM Eastern**.
- [ ] Check these schedules against existing SSIS and Solr refresh windows to avoid simultaneous staging-table changes.
- [ ] Verify the first scheduled refresh and subsequent Solr publication. Confirm failure notifications have recipients configured through `DEVELOPER_EMAILS`.

The source session is read-only. Failed batches, duplicate accessions, or an empty image catalog roll back the refresh and retain PIRO's previous catalog. Before deployment, nine focused tests and isolated SQL Server integration checks passed, and the complete source catalog query was validated read-only.
