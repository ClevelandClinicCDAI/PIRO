-- External API integration state. All datetime values are naive US/Eastern.
-- Offset minutes on deadlines/windows distinguish the repeated DST hour.
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE dbo.ExternalApiAudit (
    RequestId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiAudit PRIMARY KEY,
    ClientId varchar(32) NULL,
    KeyId varchar(32) NULL,
    Event varchar(32) NOT NULL,
    Method varchar(10) NULL,
    Route varchar(200) NULL,
    OccurredAt datetime2(6) NOT NULL,
    Actor nvarchar(100) NULL,
    SourceAddress varchar(100) NULL,
    CaseNumbersJson nvarchar(max) NULL,
    TestType nvarchar(200) NULL,
    CaseResultsJson nvarchar(max) NULL,
    RecordCount int NOT NULL,
    StatusCode int NOT NULL,
    ErrorCode varchar(64) NULL,
    ElapsedMs int NOT NULL
);
CREATE INDEX IX_ExternalApiAudit_ClientTime ON dbo.ExternalApiAudit(ClientId, OccurredAt);
GO
