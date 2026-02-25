SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE OR ALTER PROCEDURE dbo.P_SSIS_Seed_ConfigRun_CommentPlainTextCategorizationClause
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ConfigName VARCHAR(1000) = 'Query.CommentPlainText.CommentType.CategorizationClause';
    DECLARE @ConfigValue VARCHAR(4000) = '
 CASE
             WHEN COMP.NAME LIKE ''%FINAL%'' THEN ''FINAL''
             WHEN COMP.NAME LIKE ''%GROSS%'' THEN ''GROSS''
             WHEN COMP.NAME LIKE ''%INTRAOP%'' THEN ''INTRAOP''
             WHEN COMP.NAME LIKE ''%COMMENT%'' THEN ''COMMENT''
             WHEN COMP.NAME LIKE ''%SYNOPTIC%'' THEN ''SYNOPTIC''
             WHEN COMP.NAME LIKE ''%RESIDENT%'' THEN ''RESIDENT''
             WHEN COMP.NAME LIKE ''%ADDEND%'' THEN ''ADDEND''
             WHEN COMP.NAME LIKE ''%MICROSCOPIC%'' THEN ''MICROSCOPIC''
             WHEN COMP.NAME LIKE ''FLOW CYTOMETRY RESULTS'' THEN ''FINAL''
         ELSE ''OTHER''
   END';

    MERGE dbo.SSIS_ConfigRun AS Target
    USING (
        SELECT
            @ConfigName AS [Name],
            @ConfigValue AS [Val],
            CAST(1 AS BIT) AS IsActive
    ) AS Source
        ON Target.[Name] = Source.[Name]
       AND Target.IsActive = 1
    WHEN MATCHED THEN
        UPDATE
        SET Target.[Val] = Source.[Val]
    WHEN NOT MATCHED THEN
        INSERT ([Name], [Val], IsActive)
        VALUES (Source.[Name], Source.[Val], Source.IsActive);
END
GO

