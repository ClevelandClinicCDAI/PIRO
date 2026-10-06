-- PIRO external API v1: integration state only. No Case/LinkedOrder changes.
-- Run against the PIRO database BEFORE setting EXTERNAL_API_ENABLED=true.
-- Idempotent, transactional deployment. Naive Eastern storage; offsets disambiguate security deadlines.
SET XACT_ABORT ON;
BEGIN TRANSACTION;

-- Never silently reinterpret an earlier deployment's UTC data.
IF COL_LENGTH(N'dbo.ExternalApiClient', N'CreatedAtUtc') IS NOT NULL
    OR COL_LENGTH(N'dbo.ExternalApiKey', N'ExpiresAtUtc') IS NOT NULL
    OR COL_LENGTH(N'dbo.ExternalApiUsage', N'MinuteUtc') IS NOT NULL
    OR COL_LENGTH(N'dbo.ExternalApiLease', N'ExpiresAtUtc') IS NOT NULL
    OR COL_LENGTH(N'dbo.ExternalApiAudit', N'OccurredAtUtc') IS NOT NULL
BEGIN
    ;THROW 50001, 'Run migrate_external_api_eastern.sql with API workers stopped before deploying this schema.', 1;
END;

IF OBJECT_ID(N'dbo.ExternalApiClient', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ExternalApiClient (
        ClientId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiClient PRIMARY KEY,
        Name nvarchar(100) NOT NULL CONSTRAINT UQ_ExternalApiClient_Name UNIQUE,
        IsActive bit NOT NULL,
        Scope varchar(100) NOT NULL,
        CreatedAt datetime2(6) NOT NULL,
        CreatedBy nvarchar(100) NOT NULL
    );
END;

IF OBJECT_ID(N'dbo.ExternalApiKey', N'U') IS NULL
BEGIN
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
END;

IF OBJECT_ID(N'dbo.ExternalApiUsage', N'U') IS NULL
BEGIN
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
END;

IF OBJECT_ID(N'dbo.ExternalApiLease', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ExternalApiLease (
        RequestId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiLease PRIMARY KEY,
        ClientId varchar(32) NOT NULL,
        ExpiresAt datetime2(6) NOT NULL,
        ExpiresAtOffsetMinutes int NOT NULL CHECK (ExpiresAtOffsetMinutes IN (-300, -240)),
        CONSTRAINT FK_ExternalApiLease_Client FOREIGN KEY (ClientId) REFERENCES dbo.ExternalApiClient(ClientId)
    );
    CREATE INDEX IX_ExternalApiLease_ClientExpiry ON dbo.ExternalApiLease(ClientId, ExpiresAt);
END;

IF OBJECT_ID(N'dbo.ExternalApiAudit', N'U') IS NULL
BEGIN
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
END;

COMMIT TRANSACTION;

