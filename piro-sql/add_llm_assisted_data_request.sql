-- =============================================================================
-- PIRO Data Request — LLM-Assisted Extraction Migration Script
-- Run this script against your PIRO database to allow Data Requests to be
-- sourced from a Structured Data Extraction schema instead of a Saved Search.
-- Safe to re-run (idempotent).
-- =============================================================================

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

-- =============================================================================
-- V_SearchRequest: switch to LEFT JOIN so LLM-assisted requests (no Search row)
-- still appear, and surface extraction session/run info for the inbox UI.
-- =============================================================================
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
