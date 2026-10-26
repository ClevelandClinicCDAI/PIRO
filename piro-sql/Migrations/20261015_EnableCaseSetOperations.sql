/* Case set operations: run this ENTIRE script in DataGrip with your AD connection.
   Use Tx:Auto with no transaction open. Check the target database below.
   Requires ALTER on dbo.CaseSet. No tables or rows are dropped or changed.
   Only the SourceType check constraint is replaced to permit OPERATION sources.
   For a new installation, run 20261015_CreateCaseSets.sql instead (includes this).
*/
SET XACT_ABORT ON;
DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';
IF DB_NAME() <> @ExpectedDatabase
    THROW 51000, 'Wrong database selected. Check the DataGrip connection and @ExpectedDatabase.', 1;
IF @@TRANCOUNT <> 0
    THROW 51000, 'Finish the current transaction and run this script with Tx:Auto.', 1;
IF OBJECT_ID(N'dbo.CaseSet', N'U') IS NULL
   OR OBJECT_ID(N'dbo.CaseSetCase', N'U') IS NULL
   OR COL_LENGTH(N'dbo.CaseSet', N'CreationHash') IS NULL
   OR COL_LENGTH(N'dbo.CaseSet', N'SourceQuery') IS NULL
   OR COL_LENGTH(N'dbo.CaseSetCase', N'ReviewState') IS NULL
    THROW 51001, 'Current case-set tables are required. Run 20261015_CreateCaseSets.sql first.', 1;
BEGIN TRY
    BEGIN TRANSACTION;
    IF EXISTS (SELECT 1 FROM sys.check_constraints
               WHERE parent_object_id = OBJECT_ID(N'dbo.CaseSet') AND name = N'CK_CaseSet_Source')
        ALTER TABLE dbo.CaseSet DROP CONSTRAINT CK_CaseSet_Source;
    ALTER TABLE dbo.CaseSet WITH CHECK ADD CONSTRAINT CK_CaseSet_Source
        CHECK (SourceType IN ('SAVED_SEARCH','COHORT','OPERATION','MANUAL'));
    COMMIT TRANSACTION;
    SELECT DB_NAME() AS DatabaseName, N'Case set operations are ready' AS Result;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
