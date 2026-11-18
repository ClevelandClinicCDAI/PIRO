Run from `piro-api/backend` in the project's Python environment:

```powershell
$env:DATABASE = 'SQLITE'
python -m pytest tests/extraction -q
```

The default fixtures use in-memory SQLite with foreign keys enabled. These
tests override the legacy `fuzzy.db` bootstrap and do not recreate that file.

To also validate PostgreSQL transactions:

```powershell
$env:PIRO_EXTRACTION_TEST_POSTGRES = '1'
python -m pytest tests/extraction -q
```

Connection settings come from `POSTGRES_*`, or
`PIRO_EXTRACTION_TEST_POSTGRES_URL`. Only localhost is accepted. Each test
creates and removes its own `piro_extraction_test_*` schema; it does not
create/drop the database or modify existing application schemas.

The SQL Server migration
`piro-sql/add_extraction_result_comment_fk.sql` restores the development FK
after the application fix is installed. It refuses to proceed if existing
references are invalid, reports only their count, and leaves data correction
for a separate review. It also validates an existing disabled/untrusted FK.
