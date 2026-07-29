# Introduction

SQL scripts for Procedures, Data Loaders, Index creation and rebuild

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

# MISC

One-off scripts (schema tweaks, backfills, etc.) that are run manually per environment
and are NOT part of the automated deployment sequence above.

Exception: reference/lookup data scripts that a feature depends on to function (e.g.
`CytologyTerminology_Seed.sql`) are written to be idempotent and are applied
automatically by `piro-sample-data/entrypoint.sh` on every bootstrap, in addition to
being runnable manually. See that script's `apply_reference_data` function for the
current list.
