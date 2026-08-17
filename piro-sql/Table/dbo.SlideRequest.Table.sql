/****** Object:  Table [SlideRequest] ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [SlideRequest](
	[SlideRequestId] [int] IDENTITY(1,1) NOT NULL,
	[AccessionNumber] [varchar](100) NOT NULL,
	[CaseType] [varchar](20) NOT NULL,
	[Notes] [varchar](2000) NULL,
	[EPath] [bit] NOT NULL CONSTRAINT [DF_SlideRequest_EPath] DEFAULT (0),
	[SlideRoomNotes] [varchar](2000) NULL,
	[Status] [varchar](50) NOT NULL CONSTRAINT [DF_SlideRequest_Status] DEFAULT ('PENDING'),
	[UrgencyStatus] [varchar](20) NOT NULL,
	[Reason] [varchar](50) NULL,
	[DeliveryLocation] [varchar](50) NULL,
	[RequesterId] [int] NOT NULL,
	[CompletedById] [int] NULL,
	[InProcessById] [int] NULL,
	[CompletedDate] [datetime] NULL,
	[CreateDate] [datetime] NOT NULL CONSTRAINT [DF_SlideRequest_CreateDate] DEFAULT (getdate()),
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SlideRequest] PRIMARY KEY CLUSTERED 
(
	[SlideRequestId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [SlideRequest]  WITH CHECK ADD  CONSTRAINT [FK_SlideRequest_User_Requester] FOREIGN KEY([RequesterId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [SlideRequest] CHECK CONSTRAINT [FK_SlideRequest_User_Requester]
GO

ALTER TABLE [SlideRequest]  WITH CHECK ADD  CONSTRAINT [FK_SlideRequest_User_CompletedBy] FOREIGN KEY([CompletedById])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [SlideRequest] CHECK CONSTRAINT [FK_SlideRequest_User_CompletedBy]
GO

ALTER TABLE [SlideRequest]  WITH CHECK ADD  CONSTRAINT [FK_SlideRequest_User_InProcessBy] FOREIGN KEY([InProcessById])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [SlideRequest] CHECK CONSTRAINT [FK_SlideRequest_User_InProcessBy]
GO

ALTER TABLE [SlideRequest]  WITH CHECK ADD  CONSTRAINT [CK_SlideRequest_CaseType] CHECK  (([CaseType]='Surgical' OR [CaseType]='Cytology'))
GO
ALTER TABLE [SlideRequest] CHECK CONSTRAINT [CK_SlideRequest_CaseType]
GO
