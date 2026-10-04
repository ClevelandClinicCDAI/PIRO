IF OBJECT_ID(N'dbo.ConcentriqConfig', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ConcentriqConfig (
        Id int IDENTITY(1,1) NOT NULL CONSTRAINT PK_ConcentriqConfig PRIMARY KEY,
        [Key] varchar(1000) NOT NULL,
        [Value] varchar(1000) NOT NULL,
        IsActive bit NOT NULL,
        CreateDate datetime NOT NULL,
        CreateBy varchar(100) NOT NULL,
        UpdateDate datetime NULL,
        UpdateBy varchar(100) NULL
    );
END
GO
