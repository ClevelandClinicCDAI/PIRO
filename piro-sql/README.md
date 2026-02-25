# Introduction

SQL scripts for Procedures, Data Loaders, Index creation and rebuild

# Non-Docker deployment script

Use `deploy_schema.py` to deploy PIRO schema objects to a regular SQL Server instance with `sqlcmd`.

Requirements:

1. Python 3
2. `sqlcmd` installed and available in `PATH` (or pass `--sqlcmd-path`)
3. SQL login with permission to create/update database objects

Example:

```bash
python3 piro-sql/deploy_schema.py \
  --server your-sql-host \
  --port 1433 \
  --user sa \
  --password 'YourStrongPassword' \
  --database PIRO \
  --trust-server-certificate
```

Useful options:

1. `--force-reset` drops and recreates the database before deployment.
2. `--include-ssis` also deploys `SSIS/TABLES`, `SSIS/PROCS`, and `SSIS/JOBS`.
3. `--dry-run` prints commands without executing them.
4. `--scripts-root` overrides the folder that contains `Table/`, `View/`, `PLSQL/`, etc.

# Incremental PROD updates

Use `deploy_migrations.py` for incremental updates to an existing database.

How it works:

1. Reads `*.sql` files from `piro-sql/Migrations` (or `--migrations-dir`).
2. Tracks applied files in `dbo.SchemaMigrations` (configurable with `--table-name`).
3. Applies only pending scripts in sorted filename order.
4. Stores SHA-256 checksum per applied script and fails if an already-applied script was modified.

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

Baseline an already-existing PROD database:

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

# Getting Started

1. Install SQL Server Management Studio > V19
2. SQL server authenication and access

# Build and Test

Deploy the scripts in the below sequence

1. Table --> This will create all required PIRO tables along with Indexes and Keys> Due to foriegn key references, the scripts might fail. Keep executing the scripts till all pass
2. View --> --> This will created PIRO Stored Procedures
    PIRO
    SOLR
3. PLSQL --> This will created PIRO Stored Procedures
4. Function --> This will created PIRO User Functions
5. Airflow --> Below scripts are for the Airflow jobs
    PROCS --> This will created Airflow Stored Procedures
    VIEWS --> This will created Airflow feed Views
6. SSIS
    PROCS --> This will created SSIS Stored Procedures
        LOADER --> Scripts that load the data from the SSIS Staging tables to Main PIRO tables
        TRUNCATE --> Scripts that truncate the SSIS Staging tables during staging data load
    TABLES --> This will created SSIS Staging Tables
    JOBS --> SSIS job creation for delta load and full data loads
