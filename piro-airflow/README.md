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
        "description": "Case Details API call batch size",
        "value": 1000
    },
    "CONCENTRIQ_CASE_DETAIL_URL_DATA_IMPORT": {
        "description": "Case Details API URL",
        "value": "https://[concentriq_url]/api/v2/caseDetails/worklist"
    },
    "CONCENTRIQ_CERTIFICAT_NAME": {
        "description": "CONCENTRIQ SSL Cert name",
        "value": ""
    },
    "CONCENTRIQ_HEADER_AUTH": {
        "description": "BASIC Auth header",
        "value": ""
    },
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
