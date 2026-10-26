/* Run the ENTIRE script in DataGrip using AD credentials and Tx:Auto.
   Adds dbo.CaseSetSpecimen only. Does not drop tables or change existing data.
   Requires CREATE TABLE, schema and REFERENCES permissions.
   API accounts need SELECT/INSERT/UPDATE/DELETE on the new table.
*/
SET XACT_ABORT ON;
DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';
IF DB_NAME() <> @ExpectedDatabase
    THROW 51000, 'Wrong database selected. Check the DataGrip connection and @ExpectedDatabase.', 1;
IF @@TRANCOUNT <> 0
    THROW 51000, 'Finish the current transaction and run this script with Tx:Auto.', 1;
IF OBJECT_ID(N'dbo.CaseSetCase', N'U') IS NULL
    THROW 51000, 'Install the case set tables before enabling specimen selection.', 1;
BEGIN TRY
    BEGIN TRANSACTION;
-- Selected specimen IDs belong to a case within a specific case set.
IF OBJECT_ID(N'dbo.CaseSetSpecimen', N'U') IS NOT NULL
BEGIN
    IF EXISTS (
        SELECT expected.name FROM (VALUES
            (N'CaseSetId'), (N'CaseId'), (N'SpecimenId'),
            (N'SpecimenNumber'), (N'SelectedBy'), (N'SelectedAt')
        ) expected(name)
        EXCEPT SELECT name FROM sys.columns WHERE object_id=OBJECT_ID(N'dbo.CaseSetSpecimen')
    )
        THROW 51001, 'An incompatible dbo.CaseSetSpecimen already exists. Review it before deploying specimen selection.', 1;
END
ELSE
BEGIN
    CREATE TABLE dbo.CaseSetSpecimen (
        CaseSetId INT NOT NULL,
        CaseId INT NOT NULL,
        SpecimenId INT NOT NULL,
        SpecimenNumber NVARCHAR(100) NOT NULL,
        SelectedBy INT NOT NULL,
        SelectedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT PK_CaseSetSpecimen PRIMARY KEY (CaseSetId, CaseId, SpecimenId),
        CONSTRAINT FK_CaseSetSpecimen_Member FOREIGN KEY (CaseSetId, CaseId)
            REFERENCES dbo.CaseSetCase (CaseSetId, CaseId) ON DELETE CASCADE
    );
END;

    COMMIT TRANSACTION;
    SELECT DB_NAME() AS DatabaseName, N'Case set specimen selection is ready' AS Result;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
