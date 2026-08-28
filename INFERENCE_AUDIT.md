# Inference audit configuration

This application uses `ccf-inference-audit==1.0.2` from the CDAI Azure Artifacts feed. The package writes privacy-safe model and work-item events to a local SQLite outbox before delivering them to the CDAI Inference Observatory. Package installation environments must authenticate to the CDAI feed before installing `piro-airflow/requirements.txt`.

Required deployment secrets and settings:

- `INFERENCE_AUDIT_ENDPOINT`: collector base URL
- `INFERENCE_AUDIT_TOKEN`: this app/environment's unique ingest token
- `INFERENCE_AUDIT_HASH_KEY`: shared environment-specific HMAC key used to link pseudonymous subjects across apps
- `INFERENCE_AUDIT_SQLITE_PATH`: durable writable outbox path
- `INFERENCE_AUDIT_ENVIRONMENT`: `development`, `test`, or `production`
- `APP_VERSION` or `GIT_SHA`: deployed source version

Optional:

- `INFERENCE_AUDIT_BATCH_SIZE` (default `100`, maximum `500`)
- `INFERENCE_AUDIT_TIMEOUT_SECONDS` (default `2`)
- `INFERENCE_AUDIT_CA_BUNDLE` (path to a trusted collector CA bundle)

The audit client is deliberately fail-open for application work. Delivery failure leaves events queued locally with exponential backoff. Monitor `AuditClient.pending_count()` and alert on a growing backlog.

Do not add prompts, model outputs, reports, generated SQL, MRNs, accessions, names, birth dates, or unredacted exception messages to event attributes. Source identifiers are accepted only through `actor_id`, `subject_id`, or `work_item_id`, which are HMAC-hashed before persistence.
