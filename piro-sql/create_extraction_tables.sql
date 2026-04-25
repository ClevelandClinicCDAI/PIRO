-- =============================================================================
-- PIRO Extraction Suite — SQL Server Migration Script
-- Run this script against your PIRO database to create the Extraction Suite tables.
-- All tables follow the existing PIRO naming conventions (PascalCase).
-- =============================================================================

-- ExtractionSession: user's extraction workspace (draft schema + metadata)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExtractionSession')
BEGIN
    CREATE TABLE [dbo].[ExtractionSession] (
        [ExtractionSessionId] INT IDENTITY(1,1) PRIMARY KEY,
        [UserId]              INT NOT NULL,
        [Name]                NVARCHAR(255) NOT NULL,
        [SchemaJson]          NVARCHAR(MAX) NULL,
        [Status]              NVARCHAR(50) NOT NULL DEFAULT 'draft',
        [IsActive]            BIT NOT NULL DEFAULT 1,
        [CreateDate]          DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [CreateBy]            NVARCHAR(255) NOT NULL,
        [UpdateDate]          DATETIMEOFFSET NULL,
        [UpdateBy]            NVARCHAR(255) NULL,
        CONSTRAINT [FK_ExtractionSession_User]
            FOREIGN KEY ([UserId]) REFERENCES [dbo].[User]([UserId])
    );
    PRINT 'Created table ExtractionSession';
END
ELSE
    PRINT 'Table ExtractionSession already exists';

-- ExtractionRun: immutable snapshot of each extraction execution
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExtractionRun')
BEGIN
    CREATE TABLE [dbo].[ExtractionRun] (
        [ExtractionRunId]       INT IDENTITY(1,1) PRIMARY KEY,
        [ExtractionSessionId]   INT NOT NULL,
        [SchemaJson]            NVARCHAR(MAX) NOT NULL,
        [LlmProvider]           NVARCHAR(100) NOT NULL,
        [LlmModel]              NVARCHAR(255) NOT NULL,
        [Status]                NVARCHAR(50) NOT NULL DEFAULT 'pending',
        [StartedAt]             DATETIMEOFFSET NULL,
        [CompletedAt]           DATETIMEOFFSET NULL,
        [ErrorMessage]          NVARCHAR(MAX) NULL,
        [CreateDate]            DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [CreateBy]              NVARCHAR(255) NOT NULL,
        CONSTRAINT [FK_ExtractionRun_Session]
            FOREIGN KEY ([ExtractionSessionId])
            REFERENCES [dbo].[ExtractionSession]([ExtractionSessionId])
    );
    PRINT 'Created table ExtractionRun';
END
ELSE
    PRINT 'Table ExtractionRun already exists';

-- ExtractionQueue: cases queued for extraction within a session
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExtractionQueue')
BEGIN
    CREATE TABLE [dbo].[ExtractionQueue] (
        [ExtractionQueueId]     INT IDENTITY(1,1) PRIMARY KEY,
        [ExtractionSessionId]   INT NOT NULL,
        [CaseId]                INT NOT NULL,
        [Status]                NVARCHAR(50) NOT NULL DEFAULT 'pending',
        [ErrorMessage]          NVARCHAR(1000) NULL,
        [AttemptCount]          INT NOT NULL DEFAULT 0,
        [CreateDate]            DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [CreateBy]              NVARCHAR(255) NOT NULL,
        [UpdateDate]            DATETIMEOFFSET NULL,
        [UpdateBy]              NVARCHAR(255) NULL,
        CONSTRAINT [FK_ExtractionQueue_Session]
            FOREIGN KEY ([ExtractionSessionId])
            REFERENCES [dbo].[ExtractionSession]([ExtractionSessionId]),
        CONSTRAINT [FK_ExtractionQueue_Case]
            FOREIGN KEY ([CaseId]) REFERENCES [dbo].[Case]([CaseId]),
        CONSTRAINT [UQ_ExtractionQueue_Session_Case]
            UNIQUE ([ExtractionSessionId], [CaseId])
    );
    PRINT 'Created table ExtractionQueue';
END
ELSE
    PRINT 'Table ExtractionQueue already exists';

-- ExtractionResult: per-run, per-case, per-field extraction results
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExtractionResult')
BEGIN
    CREATE TABLE [dbo].[ExtractionResult] (
        [ExtractionResultId]    INT IDENTITY(1,1) PRIMARY KEY,
        [ExtractionRunId]       INT NOT NULL,
        [ExtractionSessionId]   INT NOT NULL,
        [CaseId]                INT NOT NULL,
        [FieldName]             NVARCHAR(255) NOT NULL,
        [ExtractedValue]        NVARCHAR(MAX) NULL,      -- JSON-serialized original AI value
        [ReviewedValue]         NVARCHAR(MAX) NULL,      -- JSON-serialized human-corrected value
        [Confidence]            FLOAT NULL,              -- 0.0–1.0
        [ProvenanceText]        NVARCHAR(MAX) NULL,      -- Exact quote from report
        [SourceCommentId]       INT NULL,                -- FK to CaseComment
        [ProvenanceStart]       INT NULL,                -- Char offset in labelled text
        [ProvenanceEnd]         INT NULL,                -- Char offset in labelled text
        [IsReviewed]            BIT NOT NULL DEFAULT 0,
        [ReviewedBy]            NVARCHAR(255) NULL,
        [ReviewedDate]          DATETIMEOFFSET NULL,
        [CreateDate]            DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [CreateBy]              NVARCHAR(255) NOT NULL,
        [UpdateDate]            DATETIMEOFFSET NULL,
        [UpdateBy]              NVARCHAR(255) NULL,
        CONSTRAINT [FK_ExtractionResult_Run]
            FOREIGN KEY ([ExtractionRunId])
            REFERENCES [dbo].[ExtractionRun]([ExtractionRunId]),
        CONSTRAINT [FK_ExtractionResult_Session]
            FOREIGN KEY ([ExtractionSessionId])
            REFERENCES [dbo].[ExtractionSession]([ExtractionSessionId]),
        CONSTRAINT [FK_ExtractionResult_Case]
            FOREIGN KEY ([CaseId]) REFERENCES [dbo].[Case]([CaseId]),
        CONSTRAINT [FK_ExtractionResult_Comment]
            FOREIGN KEY ([SourceCommentId])
            REFERENCES [dbo].[CaseComment]([CaseCommentId]),
        CONSTRAINT [UQ_ExtractionResult_Run_Case_Field]
            UNIQUE ([ExtractionRunId], [CaseId], [FieldName])
    );
    PRINT 'Created table ExtractionResult';
END
ELSE
    PRINT 'Table ExtractionResult already exists';

PRINT 'Migration complete.';
