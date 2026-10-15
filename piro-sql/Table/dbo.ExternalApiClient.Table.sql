-- External API integration state. All datetime values are naive US/Eastern.
-- Offset minutes on deadlines/windows distinguish the repeated DST hour.
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE dbo.ExternalApiClient (
    ClientId varchar(32) NOT NULL CONSTRAINT PK_ExternalApiClient PRIMARY KEY,
    Name nvarchar(100) NOT NULL CONSTRAINT UQ_ExternalApiClient_Name UNIQUE,
    IsActive bit NOT NULL,
    Scope varchar(100) NOT NULL,
    CreatedAt datetime2(6) NOT NULL,
    CreatedBy nvarchar(100) NOT NULL
);
GO
