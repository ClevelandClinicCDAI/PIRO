-- =============================================================================
-- ExtractionSession — configurable text sources
-- Allows users to choose which report sections (Final Diagnosis, Diagnostic
-- Comment, Addendum, Microscopic, Gross Description, etc.) are sent to the
-- LLM for extraction, per session.
-- NULL means "use the default set" (Final, Comment, Addendum, Microscopic) —
-- fully backward compatible with existing sessions.
-- Safe to re-run (idempotent).
-- =============================================================================

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
