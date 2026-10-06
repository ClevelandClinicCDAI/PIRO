-- Upgrade the initial external API UTC schema to naive US/Eastern timestamps.
-- Stop all API workers and administrative commands before running this script;
-- restart only with the matching new application code. SQL Server 2016+.
-- Preserves credentials, quotas, audit history, and exact deadline instants.
-- Repeatable: already-converted tables are skipped. No source tables change.
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH(N'dbo.ExternalApiClient', N'CreatedAtUtc') IS NOT NULL
BEGIN
    EXEC sys.sp_executesql N'UPDATE dbo.ExternalApiClient
        SET CreatedAtUtc = CONVERT(datetime2(6), CreatedAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time'');';
    EXEC sys.sp_rename N'dbo.ExternalApiClient.CreatedAtUtc', N'CreatedAt', N'COLUMN';
END;

IF COL_LENGTH(N'dbo.ExternalApiKey', N'CreatedAtUtc') IS NOT NULL
BEGIN
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiKey ADD ExpiresAtOffsetMinutes int NULL;';
    EXEC sys.sp_executesql N'UPDATE dbo.ExternalApiKey
        SET ExpiresAtOffsetMinutes = DATEPART(TZOFFSET, ExpiresAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time''),
            CreatedAtUtc = CONVERT(datetime2(6), CreatedAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time''),
            ExpiresAtUtc = CONVERT(datetime2(6), ExpiresAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time''),
            RevokedAtUtc = CONVERT(datetime2(6), RevokedAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time'');';
    EXEC sys.sp_rename N'dbo.ExternalApiKey.CreatedAtUtc', N'CreatedAt', N'COLUMN';
    EXEC sys.sp_rename N'dbo.ExternalApiKey.ExpiresAtUtc', N'ExpiresAt', N'COLUMN';
    EXEC sys.sp_rename N'dbo.ExternalApiKey.RevokedAtUtc', N'RevokedAt', N'COLUMN';
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiKey ALTER COLUMN ExpiresAtOffsetMinutes int NOT NULL;
        ALTER TABLE dbo.ExternalApiKey ADD CONSTRAINT CK_ExternalApiKey_Offset CHECK (ExpiresAtOffsetMinutes IN (-300, -240));';
END;

IF COL_LENGTH(N'dbo.ExternalApiUsage', N'MinuteUtc') IS NOT NULL
BEGIN
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiUsage ADD MinuteOffsetMinutes int NULL;';
    EXEC sys.sp_executesql N'UPDATE dbo.ExternalApiUsage
        SET MinuteOffsetMinutes = DATEPART(TZOFFSET, MinuteUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time''),
            MinuteUtc = CONVERT(datetime2(6), MinuteUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time'');';
    EXEC sys.sp_rename N'dbo.ExternalApiUsage.MinuteUtc', N'Minute', N'COLUMN';
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiUsage ALTER COLUMN MinuteOffsetMinutes int NOT NULL;
        ALTER TABLE dbo.ExternalApiUsage ADD CONSTRAINT CK_ExternalApiUsage_Offset CHECK (MinuteOffsetMinutes IN (-300, -240));';
END;

IF COL_LENGTH(N'dbo.ExternalApiLease', N'ExpiresAtUtc') IS NOT NULL
BEGIN
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiLease ADD ExpiresAtOffsetMinutes int NULL;';
    EXEC sys.sp_executesql N'UPDATE dbo.ExternalApiLease
        SET ExpiresAtOffsetMinutes = DATEPART(TZOFFSET, ExpiresAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time''),
            ExpiresAtUtc = CONVERT(datetime2(6), ExpiresAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time'');';
    EXEC sys.sp_rename N'dbo.ExternalApiLease.ExpiresAtUtc', N'ExpiresAt', N'COLUMN';
    EXEC sys.sp_executesql N'ALTER TABLE dbo.ExternalApiLease ALTER COLUMN ExpiresAtOffsetMinutes int NOT NULL;
        ALTER TABLE dbo.ExternalApiLease ADD CONSTRAINT CK_ExternalApiLease_Offset CHECK (ExpiresAtOffsetMinutes IN (-300, -240));';
END;

IF COL_LENGTH(N'dbo.ExternalApiAudit', N'OccurredAtUtc') IS NOT NULL
BEGIN
    EXEC sys.sp_executesql N'UPDATE dbo.ExternalApiAudit
        SET OccurredAtUtc = CONVERT(datetime2(6), OccurredAtUtc AT TIME ZONE ''UTC'' AT TIME ZONE ''Eastern Standard Time'');';
    EXEC sys.sp_rename N'dbo.ExternalApiAudit.OccurredAtUtc', N'OccurredAt', N'COLUMN';
END;

COMMIT TRANSACTION;
