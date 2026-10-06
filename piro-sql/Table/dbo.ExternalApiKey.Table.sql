-- External API integration state. All datetime values are naive US/Eastern.
-- Offset minutes on deadlines/windows distinguish the repeated DST hour.
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE dbo.ExternalApiKey (
    KeyId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiKey PRIMARY KEY,
    ClientId varchar(32) NOT NULL,
    SecretHash varchar(64) NOT NULL,
    CreatedAt datetime2(6) NOT NULL,
    ExpiresAt datetime2(6) NOT NULL,
    ExpiresAtOffsetMinutes int NOT NULL CHECK (ExpiresAtOffsetMinutes IN (-300, -240)),
    RevokedAt datetime2(6) NULL,
    CreatedBy nvarchar(100) NOT NULL,
    CONSTRAINT FK_ExternalApiKey_Client FOREIGN KEY (ClientId) REFERENCES dbo.ExternalApiClient(ClientId)
);
CREATE INDEX IX_ExternalApiKey_ClientId ON dbo.ExternalApiKey(ClientId);
GO
