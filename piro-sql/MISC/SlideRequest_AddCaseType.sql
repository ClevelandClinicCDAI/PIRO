IF COL_LENGTH('dbo.SlideRequest', 'CaseType') IS NULL
BEGIN
    ALTER TABLE [dbo].[SlideRequest]
    ADD [CaseType] [varchar](20) NULL;
END
GO

UPDATE [dbo].[SlideRequest]
SET [CaseType] = CASE UPPER(LEFT(LTRIM(RTRIM([AccessionNumber])), 1))
    WHEN 'S' THEN 'Surgical'
    WHEN 'C' THEN 'Cytology'
    ELSE NULL
END
WHERE [CaseType] IS NULL;
GO

IF EXISTS (
    SELECT 1
    FROM [dbo].[SlideRequest]
    WHERE [CaseType] IS NULL
)
BEGIN
    THROW 50000, 'Unable to infer SlideRequest.CaseType for one or more existing rows.', 1;
END
GO

ALTER TABLE [dbo].[SlideRequest]
ALTER COLUMN [CaseType] [varchar](20) NOT NULL;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE [name] = 'CK_SlideRequest_CaseType'
      AND [parent_object_id] = OBJECT_ID('dbo.SlideRequest')
)
BEGIN
    ALTER TABLE [dbo].[SlideRequest] WITH CHECK
    ADD CONSTRAINT [CK_SlideRequest_CaseType]
    CHECK ([CaseType] IN ('Surgical', 'Cytology'));
END
GO

ALTER TABLE [dbo].[SlideRequest]
CHECK CONSTRAINT [CK_SlideRequest_CaseType];
GO
