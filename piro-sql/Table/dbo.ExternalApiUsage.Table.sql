-- External API integration state. All datetime values are naive US/Eastern.
-- Offset minutes on deadlines/windows distinguish the repeated DST hour.
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE dbo.ExternalApiUsage (
    ClientId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiUsage PRIMARY KEY,
    QuotaDay date NOT NULL,
    ReturnedRecords int NOT NULL,
    Minute datetime2(6) NOT NULL,
    MinuteOffsetMinutes int NOT NULL CHECK (MinuteOffsetMinutes IN (-300, -240)),
    RequestCount int NOT NULL,
    CONSTRAINT FK_ExternalApiUsage_Client FOREIGN KEY (ClientId) REFERENCES dbo.ExternalApiClient(ClientId),
    CONSTRAINT CK_ExternalApiUsage_Records CHECK (ReturnedRecords >= 0),
    CONSTRAINT CK_ExternalApiUsage_Requests CHECK (RequestCount >= 0)
);
GO
