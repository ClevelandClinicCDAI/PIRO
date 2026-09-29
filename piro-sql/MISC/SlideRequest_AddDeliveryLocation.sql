IF COL_LENGTH('dbo.SlideRequest', 'DeliveryLocation') IS NULL
BEGIN
    ALTER TABLE [dbo].[SlideRequest]
    ADD [DeliveryLocation] [varchar](50) NULL;
END
GO
