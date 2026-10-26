/* Case sets -- run the ENTIRE script in one DataGrip console using your AD connection.
   Select the intended database and use Tx:Auto (no transaction already open).
   Change @ExpectedDatabase only when deliberately targeting a different database.
   Creates dbo.CaseSet, dbo.CaseSetCase and dbo.CaseSetSpecimen; enables operation sources.
   No tables or data are dropped.
   Existing Cohort/CohortCase, saved searches, and their procedures are unchanged.
   Requires CREATE TABLE and the necessary schema/REFERENCES permissions.
*/
SET XACT_ABORT ON;
DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';
IF DB_NAME() <> @ExpectedDatabase
    THROW 51000, 'Wrong database selected. Check the DataGrip connection and @ExpectedDatabase.', 1;
IF @@TRANCOUNT <> 0
    THROW 51000, 'Finish the current transaction and run this script with Tx:Auto.', 1;
IF OBJECT_ID(N'dbo.[User]', N'U') IS NULL
    THROW 51000, 'The PIRO User table is missing or not visible to this account.', 1;
BEGIN TRY
    BEGIN TRANSACTION;
-- Case sets: additive schema; an incompatible older prototype is not upgraded here.
IF OBJECT_ID(N'dbo.CaseSet', N'U') IS NOT NULL
BEGIN
    IF EXISTS (
        SELECT expected.name FROM (VALUES
        (N'CaseSetId'),
        (N'OwnerId'),
        (N'Name'),
        (N'Description'),
        (N'SourceType'),
        (N'SourceId'),
        (N'SourceName'),
        (N'SourceQuery'),
        (N'CreationKey'),
        (N'CreationHash'),
        (N'Archived'),
        (N'Revision'),
        (N'CreatedAt'),
        (N'UpdatedAt'),
        (N'CaptureState'),
        (N'CaptureCursor'),
        (N'CaptureExpected'),
        (N'CaptureSeen'),
        (N'CaptureFinishedAt'),
        (N'CaptureError'),
        (N'LastCaseId'),
        (N'ReviewFilter')
        ) expected(name)
        EXCEPT SELECT name FROM sys.columns WHERE object_id=OBJECT_ID(N'dbo.CaseSet')
    )
        THROW 51001, 'An incompatible dbo.CaseSet already exists. Review it before deploying case sets.', 1;
END
ELSE
BEGIN
CREATE TABLE dbo.[CaseSet] (
	[CaseSetId] INTEGER NOT NULL IDENTITY, 
	[OwnerId] INTEGER NOT NULL, 
	[Name] NVARCHAR(250) NOT NULL, 
	[Description] NVARCHAR(2000) NOT NULL DEFAULT '', 
	[SourceType] VARCHAR(20) NOT NULL, 
	[SourceId] INTEGER NOT NULL, 
	[SourceName] NVARCHAR(1000) NOT NULL, 
	[SourceQuery] NVARCHAR(max) NOT NULL DEFAULT '{}', 
	[CreationKey] VARCHAR(36) NOT NULL, 
	[CreationHash] VARCHAR(64) NOT NULL, 
	[Archived] BIT NOT NULL DEFAULT 0,
	[IsPublic] BIT NOT NULL DEFAULT 0,
	[SpecialtyCategory] NVARCHAR(100) NULL, 
	[Revision] INTEGER NOT NULL DEFAULT 0, 
	[CreatedAt] DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	[UpdatedAt] DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	[CaptureState] VARCHAR(20) NOT NULL DEFAULT 'CAPTURING', 
	[CaptureCursor] NVARCHAR(max) NOT NULL DEFAULT '*', 
	[CaptureExpected] INTEGER NULL, 
	[CaptureSeen] INTEGER NOT NULL DEFAULT 0, 
	[CaptureFinishedAt] DATETIME NULL, 
	[CaptureError] NVARCHAR(500) NOT NULL DEFAULT '', 
	[LastCaseId] INTEGER NULL, 
	[ReviewFilter] VARCHAR(20) NOT NULL DEFAULT 'ALL', 
	PRIMARY KEY ([CaseSetId]), 
	CONSTRAINT [UQ_CaseSet_Creation] UNIQUE ([OwnerId], [CreationKey]), 
	CONSTRAINT [CK_CaseSet_Source] CHECK (SourceType IN ('SAVED_SEARCH','COHORT','OPERATION','MANUAL')), 
	CONSTRAINT [CK_CaseSet_Capture] CHECK (CaptureState IN ('CAPTURING','READY','FAILED')), 
	CONSTRAINT [CK_CaseSet_Filter] CHECK (ReviewFilter IN ('ALL','UNREVIEWED','INCLUDED','EXCLUDED')), 
	FOREIGN KEY([OwnerId]) REFERENCES dbo.[User] ([UserId])
);
CREATE INDEX [IX_CaseSet_Owner_Archived] ON dbo.[CaseSet] ([OwnerId], [Archived]);
END;

-- Case sets: additive schema; an incompatible older prototype is not upgraded here.
IF OBJECT_ID(N'dbo.CaseSetCase', N'U') IS NOT NULL
BEGIN
    IF EXISTS (
        SELECT expected.name FROM (VALUES
        (N'CaseSetId'),
        (N'CaseId'),
        (N'Ordinal'),
        (N'ReviewState'),
        (N'ReviewedAt'),
        (N'ReviewerId'),
        (N'Revision')
        ) expected(name)
        EXCEPT SELECT name FROM sys.columns WHERE object_id=OBJECT_ID(N'dbo.CaseSetCase')
    )
        THROW 51001, 'An incompatible dbo.CaseSetCase already exists. Review it before deploying case sets.', 1;
END
ELSE
BEGIN
CREATE TABLE dbo.[CaseSetCase] (
	[CaseSetId] INTEGER NOT NULL, 
	[CaseId] INTEGER NOT NULL, 
	[Ordinal] INTEGER NOT NULL, 
	[ReviewState] VARCHAR(20) NOT NULL DEFAULT 'UNREVIEWED', 
	[ReviewedAt] DATETIME NULL, 
	[ReviewerId] INTEGER NULL, 
	[Revision] INTEGER NOT NULL DEFAULT 0, 
	PRIMARY KEY ([CaseSetId], [CaseId]), 
	CONSTRAINT [UQ_CaseSetCase_Ordinal] UNIQUE ([CaseSetId], [Ordinal]), 
	CONSTRAINT [CK_CaseSetCase_Review] CHECK (ReviewState IN ('UNREVIEWED','INCLUDED','EXCLUDED')), 
	FOREIGN KEY([CaseSetId]) REFERENCES dbo.[CaseSet] ([CaseSetId])
);
CREATE INDEX [IX_CaseSetCase_Review_Order] ON dbo.[CaseSetCase] ([CaseSetId], [ReviewState], [Ordinal]);
END;

-- Also support rerunning this installer on the first case-set release.
IF EXISTS (SELECT 1 FROM sys.check_constraints
           WHERE parent_object_id = OBJECT_ID(N'dbo.CaseSet') AND name = N'CK_CaseSet_Source')
    ALTER TABLE dbo.CaseSet DROP CONSTRAINT CK_CaseSet_Source;
ALTER TABLE dbo.CaseSet WITH CHECK ADD CONSTRAINT CK_CaseSet_Source
    CHECK (SourceType IN ('SAVED_SEARCH','COHORT','OPERATION','MANUAL'));

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

-- Sharing upgrades are additive and existing sets default to private.
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
    SELECT DB_NAME() AS DatabaseName, N'Case set tables are ready' AS Result;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
