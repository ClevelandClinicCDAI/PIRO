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

-- Upgrade an existing case-set installation without changing its memberships.
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
