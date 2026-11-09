# Introduction

The PIRO Airflow application is an implementation of scheduled jobs for the PIRO application using the [Apache Airflow](https://airflow.apache.org/) job scheduling tool.

## Getting Started

```powershell
git clone [repository url]
python -m venv env   #create a virtual environment (First time only)

pip install -r .\requirements.txt

.\env\Scripts\activate  # activate your virtual environment (Windows)

# Update the localhost_debugging.py with the function to be executed and pass the parameters
py .\localhost_debugging.py
```

## Airflow Variables

The following is an export of the Airflow Variables used in this application in JSON format.

Notes:

- `DEVELOPER_EMAILS` must be a JSON-formatted list of email strings (e.g. `["dev1@test.org", "dev2@test.org"]`).
- DAG failure notifications are enabled only when `DEVELOPER_EMAILS` contains at least one address.

{
    "CONCENTRIQ_CASE_DB_RELOAD_DATA": 0,
    "CONCENTRIQ_CASE_DETAIL_PAGE_SIZE": {
        "description": "PostgreSQL catalog batch size",
        "value": 1000
    },
    "CONCENTRIQ_MAX_CASES": 0,
    "CONCENTRIQ_DB_SERVER": "",
    "CONCENTRIQ_DB_PORT": "5432",
    "CONCENTRIQ_DB_NAME": "dx",
    "CONCENTRIQ_DB_USER": "",
    "CONCENTRIQ_DB_PASSWORD": "",
    "CONCENTRIQ_DB_SSLMODE": "prefer",
    "DEVELOPER_EMAILS": {
        "description": "Email recipients for DAG failure notifications (JSON list of strings)",
        "value": []
    },
    "MALIGNANT_ANNOTATION_MAX_RECORDS": 50000,
    "MALIGNANT_ANNOTATION_MODEL": "",
    "OLLAMA_API_URL": {
        "description": "OpenAI-compatible chat completions endpoint URL used by the malignant annotator",
        "value": "<https://[ollama_url]/api/chat/completions>"
    },
    "OLLAMA_API_VERIFY": {
        "description": "PEM file (in the certificates directory) used to verify the Ollama API HTTPS connection",
        "value": ""
    },
    "OLLAMA_API_BEARER_TOKEN": "",
    "PIRO_DB_INSTANCE": "",
    "PIRO_DB_NAME": "",
    "PIRO_DB_PASSWORD": "",
    "PIRO_DB_SERVER": "",
    "PIRO_DB_USERNAME": "",
    "RTF_TO_PLAIN_TEXT_MAX_CASES": 100000,
    "SOLR_CASE_DB_RELOAD_DATA": 0,
    "SOLR_CASE_STAFF_BATCH_DATA_UPDATE": 10000,
    "SOLR_CASE_STAFF_DB_RELOAD_DATA": 0,
    "SOLR_CASE_STAFF_URL_DATA_IMPORT": "<https://[piro_url]/solr/PIROSuggestStaff/dataimport?indent=on&wt=json&command=full-import&verbose=false&clean=false&commit=true&core=PIROSuggestStaff&name=dataimport>",
    "SOLR_CASE_STAFF_URL_DATA_UPDATE": "<https://[piro_url]/solr/PIROSuggestStaff/update?commitWithin=1000&overwrite=true&wt=json>",
    "SOLR_CASE_STAFF_URL_STATUS": "<https://[piro_url]/solr/PIROSuggestStaff/dataimport?command=status&indent=on&wt=json>",
    "SOLR_CASE_SUGGEST_BATCH_DATA_UPDATE": 10000,
    "SOLR_CASE_SUGGEST_DB_RELOAD_DATA": 0,
    "SOLR_CASE_SUGGEST_URL_DATA_COUNT": "<https://[piro_url]/solr/PIROSuggestCase/select?indent=true&q=*:*&q.op=OR&rows=0>",
    "SOLR_CASE_SUGGEST_URL_DATA_IMPORT": "<https://[piro_url]/solr/PIROSuggestCase/dataimport?indent=on&wt=json&command=full-import&verbose=false&clean=false&commit=true&core=PIROSuggestCase&name=dataimport>",
    "SOLR_CASE_SUGGEST_URL_DATA_UPDATE": "<https://[piro_url]/solr/PIROSuggestCase/update?commitWithin=1000&overwrite=true&wt=json>",
    "SOLR_CASE_SUGGEST_URL_STATUS": "<https://[piro_url]/solr/PIROSuggestCase/dataimport?command=status&indent=on&wt=json>",
    "SOLR_CASE_UPDATE_BATCH_SIZE": 1000,
    "SOLR_CASE_URL_DATA_COUNT": "<https://[piro_url]/solr/PIROCase/select?indent=true&q=*:*&q.op=OR&rows=0>",
    "SOLR_CASE_URL_DATA_IMPORT": "<https://[piro_url]/solr/PIROCase/dataimport?indent=on&wt=json&command=full-import&verbose=false&clean=false&commit=true&core=PIROCase&name=dataimport>",
    "SOLR_CASE_URL_DATA_UPDATE": "<https://[piro_url]/solr/PIROCase/update?commitWithin=1000&overwrite=true&wt=json>",
    "SOLR_CASE_URL_STATUS": "<https://[piro_url]/solr/PIROCase/dataimport?command=status&indent=on&wt=json>",
    "SOLR_CERTIFICAT_NAME": "",
    "SOLR_COHORT_BATCH_DATA_UPDATE": 10000,
    "SOLR_COHORT_DB_RELOAD_DATA": 0,
    "SOLR_COHORT_URL_DATA_IMPORT": "<https://[piro_url]/solr/PIROCohort/dataimport?_=indent=on&wt=json&command=full-import&verbose=false&clean=false&commit=true&core=PIROCohort&name=dataimport&cohortId=>",
    "SOLR_COHORT_URL_DATA_UPDATE": "<https://[piro_url]/solr/PIROCohort/update?commit=true&overwrite=true&wt=json>",
    "SOLR_COHORT_URL_STATUS": "<https://[piro_url]/solr/PIROCohort/dataimport?_=command=status&indent=on&wt=json>",
    "SOLR_HEADER_AUTH": "",
    "SSIS_DELTA_LOAD_JOB_SCHEDULE": {
        "description": "Schedule for the 'ssis_delta_load_job_schedule'.  Configured via this variable to ensure DEV & PROD DAGs don't run simultaneously.",
        "value": ""
    },
    "SSIS_PIRO_DB_INSTANCE": "",
    "SSIS_PIRO_DB_NAME": "",
    "SSIS_PIRO_DB_PASSWORD": "",
    "SSIS_PIRO_DB_SERVER": "",
    "SSIS_PIRO_DB_USERNAME": ""
}

## Concentriq whole-slide image catalog

The `concentriq_load` DAG reads PostgreSQL instead of the Concentriq HTTP API.
It runs nightly at 12:30 AM Eastern (`30 0 * * *`), with one active run at a
time and catchup disabled. The existing `solr_case_load` DAG publishes pending
search updates at 6:00 AM Eastern; this is a separate scheduled DAG.
It selects cases with at least one `public.images` record in `ready` status,
linked through `public.slides.case_detail_id` to `public.case_details.id`.
Only the Concentriq case ID, accession number, and accession date are read;
patient details and image files are not retrieved. The source connection uses
a read-only repeatable-read snapshot.

By default, each run scans the full image-bearing catalog, so images added to old cases
are picked up. The catalog is staged in a SQL Server temporary table and only
published after all batches succeed. Missing cases become inactive; matching
`CaseSolr` rows have their flags and Concentriq IDs updated, and changed rows
are queued in `CaseSolr_Delta` for the regular `solr_case_load` DAG. Existing
pending delta payloads are preserved. An empty catalog or duplicate accession
aborts the refresh and retains the previous catalog.
The Solr case uploader includes the first pending case, including queues with
only one image-availability update.

### Limit cases per run

For localhost, copy `piro-airflow/.env_template` to `piro-airflow/.env` if needed,
and set, for example:

```dotenv
AIRFLOW_VAR_CONCENTRIQ_MAX_CASES=1000
```

On Airflow servers, set the Airflow Variable **`CONCENTRIQ_MAX_CASES`** to `1000`
(without the `AIRFLOW_VAR_` prefix). An unset value or `0` keeps the existing
unlimited behavior. Negative or non-integer values fail before retrieving data.
The value limits **cases with ready images per run**, regardless of
`CONCENTRIQ_CASE_DETAIL_PAGE_SIZE`, which only controls fetch batch size.

Limited runs retrieve the next N qualifying cases in ascending Concentriq case
ID order. Progress is stored automatically in `dbo.ConcentriqConfig`, under
`CaseDetails.Get.LastCaseId`, and commits in the same transaction as the catalog
updates. A failed run retains the previous checkpoint and catalog. At the end
of a pass, retrieval starts again from the beginning so older cases are refreshed.
The checkpoint belongs to the PIRO database, so local and Airflow runs targeting
the same PIRO database share progress. The limit itself is read at task runtime.

Cases outside a limited run remain active; limited runs do not remove image
availability for cases that disappear from the source. To reconcile removals,
run once with `CONCENTRIQ_MAX_CASES=0`. That full refresh also resets progress.
The `concentriq_reset` task resets progress when deleting the catalog.
Deploy the updated `P_AIRFLOW_Concentriq_Case_Sync` and
`P_AIRFLOW_Concentriq_Case_Delete` procedures with this Python change.

Like the RTF conversion task, `concentriq_load_task` and the loader's
`get_concentriq_data` method accept an optional `max_cases_to_process` argument.
An explicit argument takes precedence over configuration; `0` explicitly
requests an unlimited run. Otherwise, `piro-airflow/.env` is loaded without
overwriting existing environment variables, and environment settings take
precedence over the Airflow Variable.

Deployment:

1. Deploy `piro-sql/Table/dbo.ConcentriqCase.Table.sql` and
   `dbo.ConcentriqConfig.Table.sql` (existing tables are retained).
2. Deploy the `P_AIRFLOW_Concentriq_Case_Load`,
   `P_AIRFLOW_Concentriq_Case_Delete`, and `P_AIRFLOW_Concentriq_Case_Sync`
   procedures from `piro-sql/Airflow/PROCS/`. Update
   `P_SSIS_LoadCaseSolr` from `piro-sql/SSIS/PROCS/LOADER-SOLR/` so subsequent
   SSIS loads respect inactive catalog records.
3. Configure the `CONCENTRIQ_DB_*` Airflow Variables listed above, or use
   their `AIRFLOW_VAR_` environment equivalents from `.env_template`.
   The inspected server does not support SSL; `prefer` is compatible.
   Use `require` or `verify-full` for a server configured with TLS.
4. Set the active `dbo.ConcentriqConfig` row with key
   `CaseDetails.Get.Enabled` to value `true` (or `1`).
5. Set API `CONCENTRIQ_URL` to the browser case-link prefix ending immediately
   before the Concentriq case ID. Run `concentriq_load`, followed by
   `solr_case_load` to publish the image filter and links.

The old API URL, Basic Auth header, and Concentriq API certificate variables
are no longer used by the catalog loader. SQL Server remains PIRO's primary
database; these PostgreSQL settings are a separate source connection.

Local inspection using the ignored repository-root override file:

```bash
cd piro-airflow
python sync_concentriq.py
```

This command only reports the source count, capped by `CONCENTRIQ_MAX_CASES`.
Inspection starts at the beginning without reading or advancing PIRO's checkpoint.
It accepts `POSTGRES_SERVER`
(including `host,port`), `POSTGRES_DATABASE`, `POSTGRES_USER`, and
`POSTGRES_PASSWORD` from `services.api.environment`. `CONCENTRIQ_DB_*`
settings are also accepted. After deploying the procedures and enabling the
configuration row, use `python sync_concentriq.py --apply` to synchronize PIRO,
using the configured limit and saved checkpoint.
It queues search updates; the Solr DAG publishes them.

Focused tests (no live databases or Airflow required):

```bash
python -m pytest tests -q
```

The optional `test_concentriq_limit_integration.py` test uses synthetic data and
the real procedures to verify successive limited runs, rollback, wraparound,
full refresh, and reset. It is skipped unless `CONCENTRIQ_TEST_POSTGRES_URL` and
`CONCENTRIQ_TEST_SQLSERVER_URL` point to empty, disposable local databases named
`concentriq_limit_test`. It creates test tables; discard those databases afterward.
