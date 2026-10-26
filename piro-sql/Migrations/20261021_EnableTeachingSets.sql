/* Run this entire script in DataGrip with your AD connection and Tx:Auto.
   Adds private-by-default sharing and a specialty category to existing case sets.
   Requires ALTER on dbo.CaseSet. Existing cases, reviews and selections are retained.
   The API also needs SELECT on dbo.Specialty and dbo.[User].
*/
SET XACT_ABORT ON;
DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';
IF DB_NAME() <> @ExpectedDatabase
    THROW 51000, 'Wrong database selected. Check the DataGrip connection and @ExpectedDatabase.', 1;
IF @@TRANCOUNT <> 0
    THROW 51000, 'Finish the current transaction and run this script with Tx:Auto.', 1;
IF OBJECT_ID(N'dbo.CaseSet', N'U') IS NULL
   OR COL_LENGTH(N'dbo.CaseSet', N'CreationHash') IS NULL
    THROW 51001, 'Current case-set tables are required. Run 20261015_CreateCaseSets.sql first.', 1;
IF COL_LENGTH(N'dbo.Specialty', N'SpecialtyCategory') IS NULL
   OR COL_LENGTH(N'dbo.Specialty', N'IsActive') IS NULL
    THROW 51001, 'The Specialty category catalog is missing or inaccessible.', 1;
BEGIN TRY
    BEGIN TRANSACTION;
    IF COL_LENGTH(N'dbo.CaseSet', N'IsPublic') IS NULL
        ALTER TABLE dbo.CaseSet ADD IsPublic BIT NOT NULL
            CONSTRAINT DF_CaseSet_IsPublic DEFAULT 0 WITH VALUES;
    IF COL_LENGTH(N'dbo.CaseSet', N'SpecialtyCategory') IS NULL
        ALTER TABLE dbo.CaseSet ADD SpecialtyCategory NVARCHAR(100) NULL;
    -- Dynamic SQL compiles after newly added columns exist in this same batch.
    IF NOT EXISTS (SELECT 1 FROM sys.check_constraints
                   WHERE parent_object_id = OBJECT_ID(N'dbo.CaseSet') AND name = N'CK_CaseSet_PublicSpecialty')
        EXEC(N'ALTER TABLE dbo.CaseSet WITH CHECK ADD CONSTRAINT CK_CaseSet_PublicSpecialty
            CHECK (IsPublic = 0 OR (SpecialtyCategory IS NOT NULL AND LTRIM(RTRIM(SpecialtyCategory)) <> ''''));');
    IF NOT EXISTS (SELECT 1 FROM sys.indexes
                   WHERE object_id = OBJECT_ID(N'dbo.CaseSet') AND name = N'IX_CaseSet_Public_Specialty')
        EXEC(N'CREATE INDEX IX_CaseSet_Public_Specialty ON dbo.CaseSet (IsPublic, Archived, SpecialtyCategory);');
    COMMIT TRANSACTION;
    SELECT DB_NAME() AS DatabaseName, N'Teaching sets are ready; existing sets remain private' AS Result;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
