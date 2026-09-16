-- =============================================================================
-- PIRO Extraction Suite — Bundled Deployment Script
--
-- Combines, in required order, every migration needed for the Extraction
-- Suite feature (Schema Builder, LLM-assisted extraction, and Data Request
-- integration):
--   1. create_extraction_tables.sql            (base tables)
--   2. add_extraction_session_text_sources.sql (per-session text sources)
--   3. add_llm_assisted_data_request.sql         (SearchRequest integration)
--   4. add_extraction_run_cancellation.sql       (cancellation flag)
--   5. add_search_request_extraction_case_snapshot.sql (request export case snapshot)
--
-- All steps are idempotent (guarded by IF NOT EXISTS / COL_LENGTH checks),
-- so this script is safe to re-run against a database at any point in its
-- migration history — already-applied steps are skipped and PRINTed as such.
--
-- Run this single file against PIRO PROD instead of the 5 individual
-- scripts.
-- =============================================================================

-- #############################################################################
-- # 1. create_extraction_tables.sql
-- #############################################################################

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
        [RunType]               NVARCHAR(50) NOT NULL DEFAULT 'full',
        [ValidationSize]        INT NULL,
        [CancellationRequested] BIT NOT NULL DEFAULT 0,
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
        [IsIncorrect]           BIT NOT NULL DEFAULT 0,
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

-- Add RunType and ValidationSize to ExtractionRun (idempotent)
IF COL_LENGTH('dbo.ExtractionRun', 'RunType') IS NULL
BEGIN
    ALTER TABLE [dbo].[ExtractionRun]
        ADD [RunType] NVARCHAR(50) NOT NULL DEFAULT 'full';
    PRINT 'Added column ExtractionRun.RunType';
END
ELSE
    PRINT 'Column ExtractionRun.RunType already exists';

IF COL_LENGTH('dbo.ExtractionRun', 'ValidationSize') IS NULL
BEGIN
    ALTER TABLE [dbo].[ExtractionRun]
        ADD [ValidationSize] INT NULL;
    PRINT 'Added column ExtractionRun.ValidationSize';
END
ELSE
    PRINT 'Column ExtractionRun.ValidationSize already exists';

-- Add CancellationRequested to ExtractionRun (idempotent — for databases created before this column was added)
IF COL_LENGTH('dbo.ExtractionRun', 'CancellationRequested') IS NULL
BEGIN
    ALTER TABLE [dbo].[ExtractionRun]
        ADD [CancellationRequested] BIT NOT NULL DEFAULT 0;
    PRINT 'Added column ExtractionRun.CancellationRequested';
END
ELSE
    PRINT 'Column ExtractionRun.CancellationRequested already exists';

-- Add IsIncorrect to ExtractionResult (idempotent — for databases created before this column was added)
IF COL_LENGTH('dbo.ExtractionResult', 'IsIncorrect') IS NULL
BEGIN
    ALTER TABLE [dbo].[ExtractionResult]
        ADD [IsIncorrect] BIT NOT NULL DEFAULT 0;
    PRINT 'Added column ExtractionResult.IsIncorrect';
END
ELSE
    PRINT 'Column ExtractionResult.IsIncorrect already exists';

PRINT 'Step 1/4 complete: create_extraction_tables';
GO

-- #############################################################################
-- # 2. add_extraction_session_text_sources.sql
-- #############################################################################

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.ExtractionSession') AND name = 'TextSources'
)
BEGIN
    ALTER TABLE [dbo].[ExtractionSession]
        ADD [TextSources] NVARCHAR(500) NULL;
    PRINT 'Added column ExtractionSession.TextSources';
END
ELSE
    PRINT 'Column ExtractionSession.TextSources already exists';
GO

PRINT 'Step 2/4 complete: add_extraction_session_text_sources';
GO

-- #############################################################################
-- # 3. add_llm_assisted_data_request.sql
-- #############################################################################

-- SearchRequest.SearchId must become optional: LLM-assisted requests have no
-- Saved Search, they reference an ExtractionSession instead.
IF EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.SearchRequest') AND name = 'SearchId' AND is_nullable = 0
)
BEGIN
    ALTER TABLE [dbo].[SearchRequest] ALTER COLUMN [SearchId] INT NULL;
    PRINT 'Altered SearchRequest.SearchId to be nullable';
END
ELSE
    PRINT 'SearchRequest.SearchId is already nullable';
GO

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.SearchRequest') AND name = 'ExtractionSessionId'
)
BEGIN
    ALTER TABLE [dbo].[SearchRequest]
        ADD [ExtractionSessionId] INT NULL
            CONSTRAINT [FK_SearchRequest_ExtractionSession]
            REFERENCES [dbo].[ExtractionSession]([ExtractionSessionId]);
    PRINT 'Added column SearchRequest.ExtractionSessionId';
END
ELSE
    PRINT 'Column SearchRequest.ExtractionSessionId already exists';
GO

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.SearchRequest') AND name = 'ExtractionRunId'
)
BEGIN
    ALTER TABLE [dbo].[SearchRequest]
        ADD [ExtractionRunId] INT NULL
            CONSTRAINT [FK_SearchRequest_ExtractionRun]
            REFERENCES [dbo].[ExtractionRun]([ExtractionRunId]);
    PRINT 'Added column SearchRequest.ExtractionRunId';
END
ELSE
    PRINT 'Column SearchRequest.ExtractionRunId already exists';
GO

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.SearchRequest') AND name = 'IsLlmAssisted'
)
BEGIN
    ALTER TABLE [dbo].[SearchRequest]
        ADD [IsLlmAssisted] BIT NOT NULL CONSTRAINT [DF_SearchRequest_IsLlmAssisted] DEFAULT (0);
    PRINT 'Added column SearchRequest.IsLlmAssisted';
END
ELSE
    PRINT 'Column SearchRequest.IsLlmAssisted already exists';
GO

-- Enforce exactly one of SearchId / ExtractionSessionId is populated.
IF NOT EXISTS (
    SELECT * FROM sys.check_constraints WHERE name = 'CK_SearchRequest_ExactlyOneSource'
)
BEGIN
    ALTER TABLE [dbo].[SearchRequest]
        ADD CONSTRAINT [CK_SearchRequest_ExactlyOneSource]
        CHECK (
            (SearchId IS NOT NULL AND ExtractionSessionId IS NULL)
            OR (SearchId IS NULL AND ExtractionSessionId IS NOT NULL)
        );
    PRINT 'Added check constraint CK_SearchRequest_ExactlyOneSource';
END
ELSE
    PRINT 'Check constraint CK_SearchRequest_ExactlyOneSource already exists';
GO

-- V_SearchRequest: switch to LEFT JOIN so LLM-assisted requests (no Search row)
-- still appear, and surface extraction session/run info for the inbox UI.
CREATE OR ALTER VIEW [V_SearchRequest] AS

SELECT SR.SearchRequestId, SR.SearchId, SR.SearchRequestReasonId,
R.ShortName SearchRequestReason, R.Code SearchRequestReasonCode,
SR.RequesterId, SR.SearchRequestStatusId,
SR.RequestName, SR.FromDate, SR.ToDate,
SR.IRB, SR.IsPediatric,
SR.RequestDocumentExtension, SR.RequestComment, SR.ApprovedDate, SR.ApprovalComment, SR.IsActive,
COALESCE(S.[Name], ES.[Name]) SearchName,
SR.IsLlmAssisted,
SR.ExtractionSessionId,
SR.ExtractionRunId,
COALESCE(ER.[Status], CASE WHEN SR.ExtractionSessionId IS NOT NULL THEN 'not_started' ELSE NULL END) ExtractionStatus,
SS.ShortName SearchRequestStatus,
dbo.F_FullName(Requester.FirstName, '', Requester.LastName) RequestedBy,
dbo.F_FullName(Approver.FirstName, '', Approver.LastName) ApprovedBy,
SR.CreateDate, SR.UpdateDate
FROM [dbo].[SearchRequest] SR
LEFT JOIN dbo.Search S on SR.SearchId = S.SearchId
LEFT JOIN dbo.ExtractionSession ES on SR.ExtractionSessionId = ES.ExtractionSessionId
LEFT JOIN dbo.ExtractionRun ER on SR.ExtractionRunId = ER.ExtractionRunId
JOIN dbo.SearchRequestReason R on SR.SearchRequestReasonId = R.SearchRequestReasonId
JOIN dbo.SearchRequestStatus SS ON SR.SearchRequestStatusId = SS.SearchRequestStatusId
LEFT JOIN dbo.[User] Requester ON SR.RequesterId = Requester.UserId
LEFT JOIN dbo.[User] Approver ON SR.ApprovedById = Approver.UserId
GO

PRINT 'Step 3/4 complete: add_llm_assisted_data_request';
GO

-- #############################################################################
-- # 4. add_extraction_run_cancellation.sql
-- #############################################################################

IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.ExtractionRun') AND name = 'CancellationRequested'
)
BEGIN
    ALTER TABLE [dbo].[ExtractionRun]
        ADD [CancellationRequested] BIT NOT NULL CONSTRAINT [DF_ExtractionRun_CancellationRequested] DEFAULT (0);
    PRINT 'Added column ExtractionRun.CancellationRequested';
END
ELSE
    PRINT 'Column ExtractionRun.CancellationRequested already exists';
GO

PRINT 'Step 4/4 complete: add_extraction_run_cancellation';
GO

-- #############################################################################
-- # 5. add_search_request_extraction_case_snapshot.sql
-- #############################################################################

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SearchRequestExtractionCase')
BEGIN
    CREATE TABLE [dbo].[SearchRequestExtractionCase] (
        [SearchRequestExtractionCaseId] INT IDENTITY(1,1) PRIMARY KEY,
        [SearchRequestId]               INT NOT NULL,
        [ExtractionRunId]               INT NOT NULL,
        [CaseId]                        INT NOT NULL,
        [SortOrder]                     INT NOT NULL,
        [CreateDate]                    DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [CreateBy]                      NVARCHAR(255) NOT NULL,
        CONSTRAINT [FK_SearchRequestExtractionCase_Request]
            FOREIGN KEY ([SearchRequestId]) REFERENCES [dbo].[SearchRequest]([SearchRequestId]),
        CONSTRAINT [FK_SearchRequestExtractionCase_Run]
            FOREIGN KEY ([ExtractionRunId]) REFERENCES [dbo].[ExtractionRun]([ExtractionRunId]),
        CONSTRAINT [FK_SearchRequestExtractionCase_Case]
            FOREIGN KEY ([CaseId]) REFERENCES [dbo].[Case]([CaseId]),
        CONSTRAINT [UQ_SearchRequestExtractionCase_Request_Run_Case]
            UNIQUE ([SearchRequestId], [ExtractionRunId], [CaseId])
    );
    PRINT 'Created table SearchRequestExtractionCase';
END
ELSE
    PRINT 'Table SearchRequestExtractionCase already exists';
GO

PRINT 'Step 5/5 complete: add_search_request_extraction_case_snapshot';
GO

PRINT 'PIRO Extraction Suite deployment complete.';
GO
