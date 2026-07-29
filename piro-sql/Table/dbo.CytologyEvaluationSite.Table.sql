/****** Object: Table [CytologyEvaluationSite] ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [CytologyEvaluationSite](
	[CytologyEvaluationSiteId] [int] IDENTITY(1,1) NOT NULL,
	[CytologyEvaluationId] [int] NOT NULL,
	[Site] [varchar](200) NULL,
	[EvalEpisodeNumber] [int] NULL,
	[Adequacy] [varchar](500) NULL,
	[DQCount] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_DQCount] DEFAULT (0),
	[PapCount] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_PapCount] DEFAULT (0),
	[ThinPrepCount] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_ThinPrepCount] DEFAULT (0),
	[CellBlockCount] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_CellBlockCount] DEFAULT (0),
	[UnstainedSlidesCount] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_UnstainedSlidesCount] DEFAULT (0),
	[SortOrder] [int] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_SortOrder] DEFAULT (0),
	[CreateDate] [datetime] NOT NULL CONSTRAINT [DF_CytologyEvaluationSite_CreateDate] DEFAULT (getdate()),
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CytologyEvaluationSite] PRIMARY KEY CLUSTERED 
(
	[CytologyEvaluationSiteId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluationSite_CytologyEvaluation] FOREIGN KEY([CytologyEvaluationId])
REFERENCES [CytologyEvaluation] ([CytologyEvaluationId])
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [FK_CytologyEvaluationSite_CytologyEvaluation]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluationSite_DQCount] CHECK (([DQCount]>=(0)))
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [CK_CytologyEvaluationSite_DQCount]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluationSite_PapCount] CHECK (([PapCount]>=(0)))
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [CK_CytologyEvaluationSite_PapCount]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluationSite_ThinPrepCount] CHECK (([ThinPrepCount]>=(0)))
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [CK_CytologyEvaluationSite_ThinPrepCount]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluationSite_CellBlockCount] CHECK (([CellBlockCount]>=(0)))
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [CK_CytologyEvaluationSite_CellBlockCount]
GO

ALTER TABLE [CytologyEvaluationSite] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluationSite_UnstainedSlidesCount] CHECK (([UnstainedSlidesCount]>=(0)))
GO
ALTER TABLE [CytologyEvaluationSite] CHECK CONSTRAINT [CK_CytologyEvaluationSite_UnstainedSlidesCount]
GO
