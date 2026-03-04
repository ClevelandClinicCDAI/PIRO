SET NOCOUNT ON;
GO

IF OBJECT_ID('[dbo].[CommentType]', 'U') IS NOT NULL
BEGIN
    IF EXISTS (SELECT 1 FROM [dbo].[CommentType] WHERE [Code] = 'MICROSCOPIC')
    BEGIN
        UPDATE [dbo].[CommentType]
           SET [ShortName] = 'Microscopic',
               [DESCRIPTION] = 'Microscopic description',
               [DataLabReference] = 'COMMENT-MICROSCOPIC',
               [IsActive] = 1,
               [UpdateDate] = GETDATE(),
               [UpdateBy] = USER
         WHERE [Code] = 'MICROSCOPIC';
    END
    ELSE
    BEGIN
        INSERT INTO [dbo].[CommentType]
        (
            [ShortName],
            [Code],
            [DESCRIPTION],
            [DataLabReference],
            [ETLSource],
            [IsActive],
            [CreateDate],
            [CreateBy],
            [UpdateDate],
            [UpdateBy]
        )
        VALUES
        (
            'Microscopic',
            'MICROSCOPIC',
            'Microscopic description',
            'COMMENT-MICROSCOPIC',
            'Migration',
            1,
            GETDATE(),
            USER,
            GETDATE(),
            USER
        );
    END
END
GO

IF OBJECT_ID('[dbo].[SSIS_ConfigRun]', 'U') IS NOT NULL
BEGIN
    IF COL_LENGTH('dbo.SSIS_ConfigRun', 'Name') IS NOT NULL
       AND COL_LENGTH('dbo.SSIS_ConfigRun', 'Name') < 1000
    BEGIN
        ALTER TABLE [dbo].[SSIS_ConfigRun] ALTER COLUMN [Name] VARCHAR(1000) NOT NULL;
    END;

    IF COL_LENGTH('dbo.SSIS_ConfigRun', 'Val') IS NOT NULL
       AND COL_LENGTH('dbo.SSIS_ConfigRun', 'Val') < 4000
    BEGIN
        ALTER TABLE [dbo].[SSIS_ConfigRun] ALTER COLUMN [Val] VARCHAR(4000) NOT NULL;
    END;

    DECLARE @CategorizationClause VARCHAR(4000) =
        'CASE WHEN COMP.NAME LIKE ''%FINAL%'' THEN ''FINAL'' WHEN COMP.NAME LIKE ''%GROSS%'' THEN ''GROSS'' WHEN COMP.NAME LIKE ''%INTRAOP%'' THEN ''INTRAOP'' WHEN COMP.NAME LIKE ''%COMMENT%'' THEN ''COMMENT'' WHEN COMP.NAME LIKE ''%SYNOPTIC%'' THEN ''SYNOPTIC'' WHEN COMP.NAME LIKE ''%RESIDENT%'' THEN ''RESIDENT'' WHEN COMP.NAME LIKE ''%ADDEND%'' THEN ''ADDEND'' WHEN COMP.NAME LIKE ''%MICROSCOPIC%'' THEN ''MICROSCOPIC'' WHEN COMP.NAME LIKE ''FLOW CYTOMETRY RESULTS'' THEN ''FINAL'' ELSE ''OTHER'' END';

    IF EXISTS
    (
        SELECT 1
          FROM [dbo].[SSIS_ConfigRun]
         WHERE [Name] = 'Query.CommentPlainText.CommentType.CategorizationClause'
    )
    BEGIN
        UPDATE [dbo].[SSIS_ConfigRun]
           SET [Val] = @CategorizationClause,
               [IsActive] = 1
         WHERE [Name] = 'Query.CommentPlainText.CommentType.CategorizationClause';
    END
    ELSE
    BEGIN
        INSERT INTO [dbo].[SSIS_ConfigRun] ([Name], [Val], [IsActive])
        VALUES
        (
            'Query.CommentPlainText.CommentType.CategorizationClause',
            @CategorizationClause,
            1
        );
    END
END
GO
