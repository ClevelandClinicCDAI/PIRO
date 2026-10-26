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
