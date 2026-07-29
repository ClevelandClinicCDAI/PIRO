/****** Object: Table [CytologyEvaluation] ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [CytologyEvaluation](
	[CytologyEvaluationId] [int] IDENTITY(1,1) NOT NULL,
	[PatientIdentifiers] [varchar](500) NULL,
	[ProcedureType] [varchar](100) NULL,
	[ProcedurePerformedBy] [varchar](100) NULL,
	[EvaluationPerformedBy] [varchar](100) NULL,
	[ViaTelecytology] [bit] NULL,
	[ReadLocation] [varchar](200) NULL,
	[ProcedureLocation] [varchar](200) NULL,
	[AssignedToUserId] [int] NULL,
	[ClinicalHistory] [varchar](2000) NULL,
	[Notes] [varchar](2000) NULL,
	[PatientHistory] [varchar](max) NULL,
	[CytologyPersonnelUserId] [int] NULL,
	[PathologistUserId] [int] NULL,
	[FellowUserId] [int] NULL,
	[ResidentUserId] [int] NULL,
	[TotalTimeSpentMinutes] [int] NULL,
	[Status] [varchar](30) NOT NULL CONSTRAINT [DF_CytologyEvaluation_Status] DEFAULT ('Draft'),
	[PrelimVerifierId] [int] NULL,
	[PrelimVerifiedDate] [datetime] NULL,
	[FinalVerifierId] [int] NULL,
	[FinalVerifiedDate] [datetime] NULL,
	[CreateDate] [datetime] NOT NULL CONSTRAINT [DF_CytologyEvaluation_CreateDate] DEFAULT (getdate()),
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CytologyEvaluation] PRIMARY KEY CLUSTERED 
(
	[CytologyEvaluationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_AssignedTo] FOREIGN KEY([AssignedToUserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_AssignedTo]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_CytologyPersonnel] FOREIGN KEY([CytologyPersonnelUserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_CytologyPersonnel]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_Pathologist] FOREIGN KEY([PathologistUserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_Pathologist]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_Fellow] FOREIGN KEY([FellowUserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_Fellow]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_Resident] FOREIGN KEY([ResidentUserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_Resident]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_PrelimVerifier] FOREIGN KEY([PrelimVerifierId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_PrelimVerifier]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [FK_CytologyEvaluation_User_FinalVerifier] FOREIGN KEY([FinalVerifierId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [FK_CytologyEvaluation_User_FinalVerifier]
GO

ALTER TABLE [CytologyEvaluation] WITH CHECK ADD CONSTRAINT [CK_CytologyEvaluation_Status] CHECK (([Status]='Draft' OR [Status]='Prelim Verified' OR [Status]='Final Verified'))
GO
ALTER TABLE [CytologyEvaluation] CHECK CONSTRAINT [CK_CytologyEvaluation_Status]
GO
