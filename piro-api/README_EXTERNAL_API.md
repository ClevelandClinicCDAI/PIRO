# PIRO external API v1

The external API reads current linked-order results for an explicit list of case
numbers. It uses PIRO-managed application credentials, independently of the
human-user `AUTH_MODE`. It runs in the existing API deployment and uses its
hostname and TLS termination.

## Deployment

1. Install the updated `piro-api/core_requirements.txt`.
2. Run [deploy_external_api.sql](../piro-sql/deploy_external_api.sql) against
   the PIRO SQL Server database. It creates only five integration tables in a
   transaction and can be run again. Individual definitions are also maintained
   in `piro-sql/Table/dbo.ExternalApi*.Table.sql`. It does not change clinical
   tables or ETL.
3. Provision an integration and issue a key using the commands below.
4. Set `EXTERNAL_API_ENABLED=true` in the API environment and restart all API
   workers. For Compose, the root `.env` variables are forwarded to the API.
   For a direct deployment, use `backend/.env` or process environment variables.
5. Confirm the actual public route through your reverse proxy. The backend
   route is `/external/v1/linked-orders/search`; the repository's UI proxy adds
   `/api`, producing `/api/external/v1/linked-orders/search`.
6. Schedule the consuming Airflow DAG outside PIRO's linked-order load window.
   The consumer owns comparison, corrections, and destination deletion logic.

The feature defaults to disabled. Disable it and restart workers to roll back
exposure without deleting credentials, counters, or audit history. The legacy
UI routes remain unchanged. No production schema changes run automatically on
application startup.

The UI and external API use the shared `backend/db/engine.py` engine factory
and existing database connection settings. The external API retains a separate
pool so its statement timeout does not affect UI requests. SQL Server is the
production backend; localhost PostgreSQL is used for external functional tests.
The API implementation lives in `backend/apis/external_api`, with its own
schemas, authentication, and application boundary. A restricted database identity needs SELECT on
`Case` and `LinkedOrder`, plus access to the integration tables appropriate to
authentication, quota updates, leases, and audit insertion. Administrator
commands also write clients and credentials.

## Administrator commands

Run these from `piro-api/backend` with the API's Python environment and database
configuration. These commands do not require LDAP or OAuth authentication.
Operating-system/database access controls determine who may run them.

```text
python -m apis.external_api.admin create-client --name "External Airflow" --actor "administrator"
python -m apis.external_api.admin issue-key --client-id <client_id> --expires-days 90 --actor "administrator"
python -m apis.external_api.admin list-clients
python -m apis.external_api.admin list-keys --client-id <client_id>
python -m apis.external_api.admin revoke-key --key-id <key_id> --actor "administrator"
python -m apis.external_api.admin disable-client --client-id <client_id> --actor "administrator"
python -m apis.external_api.admin enable-client --client-id <client_id> --actor "administrator"
```

`issue-key` prints the secret once. Store it in the external Airflow instance's
connection/secrets backend; never commit it or put it in a URL. PIRO stores a
SHA-256 verifier of the randomly generated 256-bit credential, not its plaintext.
The key ID is an identifier, not a credential. List commands never reveal a
secret or hash. The actor defaults to the operating-system username if omitted.

Keys expire after 90 days by default; `--expires-days` accepts 1 through 3660.
To rotate, issue another key, update the consumer, verify it works, then revoke
the old key. Both keys share the integration's limits. Revocation or disabling
is checked on subsequent requests/admissions; an already admitted request may
finish. Enable-client does not un-revoke keys.

## Request and contract

```http
POST /api/external/v1/linked-orders/search
X-API-Key: <secret>
Content-Type: application/json
```

```json
{
  "case_numbers": ["S26-12345", "S26-67890"],
  "test_type": "PD-L1"
}
```

- `case_numbers` is required, nonempty, and bounded by the deployment limit.
  Each value is a string of at most 100 characters. Surrounding whitespace is
  removed; identical submitted values are deduplicated. Blank/control-character
  values, nonstrings, and unknown request fields are rejected.
- Matching is exact under the existing `Case.CaseNumber` SQL collation.
  All PIRO cases with a matching number contribute results, including inactive
  cases. No hospital, cohort, or human-user attestation filter is applied.
- `test_type` may be omitted or null. If supplied it must be a nonblank string
  of at most 200 characters. It is a literal case-insensitive substring across
  `ComponentName`, `ComponentExternalName`, or `ProcedureDesc`.
  SQL Server uses `Latin1_General_100_CI_AS` for those comparisons (case
  insensitive, accent sensitive). Percent, underscore, backslash, and opening
  bracket characters are escaped, not interpreted as user-supplied LIKE syntax.
- Linked orders without a matching CaseId are excluded. Unmatched case numbers
  contribute no data rows. Identical result rows are preserved.
- Result order is not a durable identity. No source row ID or incremental
  watermark is exposed. Consumers should compare records as a multiset.

A successful response is complete for the requested batch and filter:

```json
{
  "request_id": "d0ea1ace969b4ec598a5a8e7100c69b8",
  "data": [
    {
      "CaseNumber": "S26-12345",
      "ComponentName": "PD-L1",
      "ComponentExternalName": null,
      "ProcedureDesc": "PD-L1 assay",
      "DefaultUnit": "%",
      "OrdValue": "12.34",
      "OrdNumValue": "12.34000"
    }
  ],
  "record_count": 1,
  "cases": [
    {"CaseNumber": "S26-12345", "status": "matched", "record_count": 1},
    {"CaseNumber": "S26-67890", "status": "case_not_found", "record_count": 0}
  ]
}
```

Every data record contains exactly the seven fields shown above. CaseNumber
comes from `Case`; the other fields come from `LinkedOrder`. Null values remain
JSON null. OrdNumValue is a decimal string with five fractional digits, preserving
SQL decimal(38,5) precision; parse it with Python's `decimal.Decimal` if needed.

Each distinct submitted case number has a summary:

| Status | Meaning |
| --- | --- |
| matched | One or more matching linked orders were returned. |
| no_matching_orders | PIRO has the case number, but no orders match the filter (or no linked orders exist). |
| case_not_found | PIRO has no case matching that submitted number. |

The summary echoes the trimmed submitted number; data rows contain the stored
number. If two submitted strings compare equal under the database collation,
their summaries can cover the same records; the data array does not duplicate
rows because of those aliases.

Only reconcile a case after a successful complete response. The API reads the
currently committed source data; it does not provide a historical snapshot or
a guarantee against the delete/reinsert phase of a concurrent ETL load.
Coordination of job schedules is the agreed consistency mechanism. Do not
interpret HTTP failures as missing data or perform destination deletions from
failed batches. The raw-high/raw-low loader bug is outside this endpoint's fields
and was not changed.

## Limits and errors

| Environment variable | Default |
| --- | ---: |
| EXTERNAL_API_ENABLED | false |
| EXTERNAL_API_MAX_CASES | 100 |
| EXTERNAL_API_MAX_RECORDS | 5000 |
| EXTERNAL_API_DAILY_RECORDS | 50000 |
| EXTERNAL_API_REQUESTS_PER_MINUTE | 30 |
| EXTERNAL_API_MAX_CONCURRENT | 2 |
| EXTERNAL_API_QUERY_TIMEOUT_SECONDS | 30 |
| EXTERNAL_API_MAX_BODY_BYTES | 65536 |

Limits apply per integration, shared across credentials, processes, and workers.
The request rate uses fixed minute windows, distinguished by Eastern time and
UTC offset during the repeated fall-back hour. The returned-record quota resets
at midnight in `America/New_York`, including daylight-saving transitions.
Successful retries count again. A response whose complete result exceeds the
remaining quota is rejected in full and does not consume returned-record quota.
A committed response that is lost in transport is still charged/audited.

The database query timeout applies to each statement in the separate pool
(pyodbc timeout on SQL Server, statement_timeout on PostgreSQL). Concurrency
leases expire after twice that timeout plus 60 seconds, so
a crashed worker cannot retain a slot indefinitely. A worker whose lease has
expired cannot publish its old result. Database locks serialize admission and
quota completion, but are not held while reading clinical results.

No result is silently truncated. A request over the record limit must be split
into smaller case batches or use a narrower test_type. If one case alone exceeds
the limit, refine its filter or have the administrator review/tune the limit.
There is also a matching-case lookup cap equal to the record limit to bound
pathological duplicate case numbers. There is no record-level pagination in v1.

Errors use a stable envelope:

```json
{
  "request_id": "d0ea1ace969b4ec598a5a8e7100c69b8",
  "error": {
    "code": "result_limit_exceeded",
    "message": "Complete results exceed the batch limit; split case_numbers or narrow test_type."
  }
}
```

| HTTP | Codes / handling |
| --- | --- |
| 401 | invalid_api_key; provision/update the credential. |
| 403 | integration_disabled, insufficient_scope; contact the administrator. |
| 404 | external_api_disabled, or unavailable route. |
| 413 | request_too_large; reduce the request body. |
| 422 | invalid_request, too_many_cases, case_lookup_limit_exceeded, result_limit_exceeded; correct/split the request. |
| 429 | rate_limit_exceeded, concurrency_limit_exceeded, daily_quota_exceeded; honor Retry-After and bound retries. |
| 500 | internal_error; retry the complete batch with a bounded policy. |
| 503 | database_unavailable, audit_unavailable, request_lease_expired; retry the complete batch. |

Responses include `X-Request-ID` and `Cache-Control: no-store`; retryable limits
and temporary service failures include `Retry-After`. Credentials belong only in
`X-API-Key`. UI JWTs do not authorize this endpoint, and API keys do not authorize
UI endpoints. The external API never issues UI Refreshtoken headers.

## Audit and operation

`ExternalApiAudit` records the integration/key identifiers, API route/method,
request ID, submitted cases, filter, per-case counts, total rows, outcome,
execution time, and caller address. Administrative changes record the actor.
Authentication failures are recorded without falsely attributing an unverified
credential to a client. No credential or clinical result values are stored in
audits. Submitted case numbers are sensitive and belong in protected audit
storage.

Audit and successful quota accounting commit together before a data response is
released. If the audit database is unavailable, no successful data response is
returned. Application logs contain IDs/status/timing and exception types, not
request bodies, API keys, SQL parameters, or clinical values. Use trusted proxy
configuration for forwarded source addresses; the application does not trust
arbitrary X-Forwarded-For headers itself.

All database datetime columns (`CreatedAt`, `ExpiresAt`, `RevokedAt`, `Minute`,
and `OccurredAt`) store naive `America/New_York` time, consistent with PIRO.
Quota days use that same calendar. API key/lease deadlines additionally store
`ExpiresAtOffsetMinutes`; the minute rate window stores `MinuteOffsetMinutes`.
These small offset fields distinguish the two occurrences of the fall-back hour.
Expiry and elapsed-time arithmetic use aware instants internally, preventing
expired keys from becoming valid again or leases expiring an hour too early/late.
Key lifetimes remain exact multiples of 24 hours; CLI `expires_at` includes the
Eastern offset. Audit timestamps can be read directly as Eastern wall time:

```sql
SELECT RequestId, ClientId, StatusCode, RecordCount, OccurredAt
FROM dbo.ExternalApiAudit
ORDER BY OccurredAt DESC;
```

Like other naive PIRO timestamps, audit wall times alone do not distinguish
chronological order within the repeated fall-back hour.

No automatic retention/purge job is introduced. Administrators should apply
the organization's existing audit retention policy. Revoked credentials and
client identities are retained for traceability.

## Airflow consumer example

Resolve the key from an Airflow connection/secrets backend before calling this
function. Use an authenticated internal HTTPS URL with normal certificate
verification. Configure proxy/read timeouts to allow the bounded database work.

```python
from decimal import Decimal
import requests

def fetch_linked_orders(api_base, api_key, case_numbers, test_type=None):
    case_numbers = list(dict.fromkeys(number.strip() for number in case_numbers))
    results, outcomes = [], []
    with requests.Session() as session:
        session.headers["X-API-Key"] = api_key
        for start in range(0, len(case_numbers), 100):
            payload = {"case_numbers": case_numbers[start:start + 100]}
            if test_type is not None:
                payload["test_type"] = test_type
            response = session.post(
                api_base.rstrip("/") + "/external/v1/linked-orders/search",
                json=payload, timeout=(10, 90),
            )
            response.raise_for_status()
            batch = response.json()
            if len(results) + batch["record_count"] > 50000:
                raise RuntimeError("Consumer record budget exceeded")
            results.extend(batch["data"])
            outcomes.extend(batch["cases"])
    # Reconcile only after the required complete batches succeed.
    return results, outcomes

# Decimal(record["OrdNumValue"]) if record["OrdNumValue"] is not None else None
```

`api_base` includes `/api` when using the bundled proxy. The example deliberately
raises on errors. The DAG can split 422 overflow batches and use bounded retries
for 429/503, honoring Retry-After. Avoid retrying a whole successful extract
unnecessarily because those returned rows count again toward the daily budget.

## Verification and compatibility

The external regression suite is part of `backend/tests/external_api`. It uses
an existing localhost PostgreSQL database and creates/drops only uniquely named
`piro_external_test_<uuid>` schemas. The test role needs permission to create
schemas. The database itself and existing tables are never created or dropped.
Set `PIRO_EXTERNAL_TEST_POSTGRES_URL` to a localhost SQLAlchemy PostgreSQL URL,
or use `POSTGRES_USER` (postgres), `POSTGRES_PASSWORD`,
`POSTGRES_SERVER` (localhost), `POSTGRES_PORT` (5432), and `POSTGRES_DB` (testdb). Keep credentials in the test
process environment or an existing protected configuration, not source control.

From the repository root, run:

```text
python scripts/test_external_api.py
python scripts/test_external_api.py --full-suite
```

The runner supplies test-only application settings and the backend import path.
It starts no containers and changes no environment files. The existing backend
tests retain their SQLite fixtures; the new external suite overrides that
bootstrap with PostgreSQL schemas. Authentication, API contracts, concurrent
quotas, exact decimal precision, statement timeouts, and DST behavior run on
PostgreSQL. With the same application settings and backend PYTHONPATH set,
standard pytest discovery also works:

```text
python -m pytest piro-api/backend/tests -q
```

SQL Server-specific deployment, migration, and collation tests remain opt-in.
They use a uniquely named temporary schema and never modify dbo clinical tables.
To include them, configure a NONPRODUCTION database and explicitly allow schema
creation:

```text
PIRO_EXTERNAL_TEST_DATABASE_URL=<nonproduction mssql+pyodbc SQLAlchemy URL>
PIRO_EXTERNAL_TEST_ALLOW_SCHEMA_CREATE=yes
```

Measure representative 100-case batches and inspect SQL Server query plans in
the deployment environment. Existing CaseNumber and LinkedOrder.CaseId indexes
are used as the starting point; no speculative source indexes are added.

The independent OpenAPI document is at `/external/v1/openapi.json`, with Swagger
at `/external/v1/docs` (prepend the proxy prefix when appropriate). These
metadata routes are available without a key while the feature is enabled.
They are not merged into the UI OpenAPI document. Breaking contract changes
require a new external version; v1 remains stable.
