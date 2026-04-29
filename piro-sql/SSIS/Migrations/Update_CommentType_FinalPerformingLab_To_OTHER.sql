-- Reclassify "Final Performing Lab" comment types from FINAL to OTHER.
--
-- Adds two guards before the broad %FINAL% catch-all in the active
-- Query.CommentPlainText.CommentType.CategorizationClause configuration:
--   %FINAL PERFORMING LAB%  -> OTHER
--   %FINALPERFORMINGLAB%    -> OTHER
--
-- Idempotent: the WHERE clause ensures this UPDATE is a no-op if the
-- guards are already present.

UPDATE dbo.SSIS_ConfigRun
SET Val = REPLACE(
    Val,
    'CASE WHEN COMP.NAME LIKE ''%FINAL%'' THEN ''FINAL''',
    'CASE WHEN COMP.NAME LIKE ''%FINAL PERFORMING LAB%'' THEN ''OTHER'' WHEN COMP.NAME LIKE ''%FINALPERFORMINGLAB%'' THEN ''OTHER'' WHEN COMP.NAME LIKE ''%FINAL%'' THEN ''FINAL'''
)
WHERE [Name] = 'Query.CommentPlainText.CommentType.CategorizationClause'
  AND IsActive = 1
  AND Val NOT LIKE '%FINAL PERFORMING LAB%';
