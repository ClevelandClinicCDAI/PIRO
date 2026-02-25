# SQL Migrations

Put incremental SQL migration files in this folder.

Naming convention (recommended):

1. `YYYY-MM-DD_NNN_short_description.sql`
2. Example: `2026-02-25_001_add_case_isarchived.sql`

Guidelines:

1. Do not edit old migration files after they are applied.
2. Use idempotent SQL where practical (`IF ... THEN ALTER ...`, `CREATE OR ALTER ...`).
3. Keep each migration focused and reversible if possible.

Apply pending migrations:

```bash
python3 piro-sql/deploy_migrations.py \
  --server your-sql-host \
  --port 1433 \
  --user sa \
  --password 'YourStrongPassword' \
  --database PIRO \
  --trust-server-certificate
```

Baseline an existing PROD database (record scripts as applied without executing):

```bash
python3 piro-sql/deploy_migrations.py \
  --server your-sql-host \
  --port 1433 \
  --user sa \
  --password 'YourStrongPassword' \
  --database PIRO \
  --baseline \
  --trust-server-certificate
```
