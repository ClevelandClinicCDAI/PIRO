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
