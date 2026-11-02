IF OBJECT_ID(N'dbo.ConcentriqCase', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ConcentriqCase (
        Id int IDENTITY(1,1) NOT NULL CONSTRAINT PK_ConcentriqCase PRIMARY KEY,
        ConcentriqCaseId int NOT NULL,
        CaseId int NOT NULL,
        CaseNumber varchar(100) NOT NULL,
        AccessionDate datetime NULL,
        IsActive bit NOT NULL,
        CreateDate datetime NOT NULL,
        CreateBy varchar(100) NOT NULL,
        UpdateDate datetime NULL,
        UpdateBy varchar(100) NULL
    );
    CREATE INDEX IX_ConcentriqCase_CaseId ON dbo.ConcentriqCase(CaseId);
END
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE object_id = OBJECT_ID('dbo.ConcentriqCase')
                 AND name = 'IX_ConcentriqCase_CaseNumber')
    CREATE INDEX IX_ConcentriqCase_CaseNumber
        ON dbo.ConcentriqCase(CaseNumber) INCLUDE (ConcentriqCaseId, IsActive);
GO
