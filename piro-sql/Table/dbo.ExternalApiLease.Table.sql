-- External API integration state. All datetime values are naive US/Eastern.
-- Offset minutes on deadlines/windows distinguish the repeated DST hour.
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE dbo.ExternalApiLease (
    RequestId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiLease PRIMARY KEY,
    ClientId varchar(32) NOT NULL,
    ExpiresAt datetime2(6) NOT NULL,
    ExpiresAtOffsetMinutes int NOT NULL CHECK (ExpiresAtOffsetMinutes IN (-300, -240)),
    CONSTRAINT FK_ExternalApiLease_Client FOREIGN KEY (ClientId) REFERENCES dbo.ExternalApiClient(ClientId)
);
CREATE INDEX IX_ExternalApiLease_ClientExpiry ON dbo.ExternalApiLease(ClientId, ExpiresAt);
GO
