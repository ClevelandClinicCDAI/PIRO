/****** Object: Table [CytologyTerminology] ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [CytologyTerminology](
	[CytologyTerminologyId] [int] IDENTITY(1,1) NOT NULL,
	[Category] [varchar](50) NOT NULL,
	[Value] [varchar](200) NOT NULL,
	[SortOrder] [int] NOT NULL CONSTRAINT [DF_CytologyTerminology_SortOrder] DEFAULT (0),
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_CytologyTerminology_IsActive] DEFAULT (1),
	[CreateDate] [datetime] NOT NULL CONSTRAINT [DF_CytologyTerminology_CreateDate] DEFAULT (getdate()),
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CytologyTerminology] PRIMARY KEY CLUSTERED 
(
	[CytologyTerminologyId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [CytologyTerminology] WITH CHECK ADD CONSTRAINT [CK_CytologyTerminology_Category] CHECK (([Category]='ProcedureType' OR [Category]='ReadLocation' OR [Category]='ProcedureLocation' OR [Category]='Site' OR [Category]='Adequacy'))
GO
ALTER TABLE [CytologyTerminology] CHECK CONSTRAINT [CK_CytologyTerminology_Category]
GO

CREATE NONCLUSTERED INDEX [IX_CytologyTerminology_Category] ON [CytologyTerminology]
(
	[Category] ASC,
	[IsActive] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
