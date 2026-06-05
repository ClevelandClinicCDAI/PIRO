IF COL_LENGTH('dbo.SlideRequest', 'Reason') IS NULL
BEGIN
    ALTER TABLE [dbo].[SlideRequest]
    ADD [Reason] [varchar](50) NULL;
END
GO
