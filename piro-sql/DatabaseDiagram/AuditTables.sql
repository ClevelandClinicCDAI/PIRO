/****** Object:  Table [AuditCaseAnnotation]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AuditCaseAnnotation](
	[AuditCaseAnnotationId] [int] IDENTITY(1,1) NOT NULL,
	[CaseAnnotationId] [int] NOT NULL,
	[AnnotationId] [int] NOT NULL,
	[CaseId] [int] NOT NULL,
	[AnnotationConfigurationId] [int] NOT NULL,
	[ModelName] [varchar](50) NOT NULL,
	[SourceValue] [varchar](50) NOT NULL,
	[AnnotationValue] [varchar](50) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AuditCaseAnnotation] PRIMARY KEY CLUSTERED 
(
	[AuditCaseAnnotationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_AuditCaseAnnotation_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_AuditCaseAnnotation_CaseId] ON [AuditCaseAnnotation]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_AuditCaseAnnotation_CaseId_AnnotationConfigurationId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_AuditCaseAnnotation_CaseId_AnnotationConfigurationId] ON [AuditCaseAnnotation]
(
	[CaseId] ASC,
	[AnnotationConfigurationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO




/****** Object:  Table [AuditTrailCase]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AuditTrailCase](
	[AuditTrailCaseId] [int] IDENTITY(1,1) NOT NULL,
	[AuditTrailSearchId] [int] NOT NULL,
	[UserId] [int] NOT NULL,
	[CaseId] [int] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AuditTrailCase] PRIMARY KEY CLUSTERED 
(
	[AuditTrailCaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [AuditTrailCase]  WITH CHECK ADD  CONSTRAINT [FK_AuditTrailCase_AuditTrailCase] FOREIGN KEY([AuditTrailCaseId])
REFERENCES [AuditTrailCase] ([AuditTrailCaseId])
GO
ALTER TABLE [AuditTrailCase] CHECK CONSTRAINT [FK_AuditTrailCase_AuditTrailCase]
GO
ALTER TABLE [AuditTrailCase]  WITH CHECK ADD  CONSTRAINT [FK_AuditTrailCase_Case] FOREIGN KEY([CaseId])
REFERENCES [Case] ([CaseId])
GO
ALTER TABLE [AuditTrailCase] CHECK CONSTRAINT [FK_AuditTrailCase_Case]
GO
ALTER TABLE [AuditTrailCase]  WITH CHECK ADD  CONSTRAINT [FK_AuditTrailCase_User] FOREIGN KEY([UserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [AuditTrailCase] CHECK CONSTRAINT [FK_AuditTrailCase_User]
GO





/****** Object:  Table [AuditTrailCaseInfo]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AuditTrailCaseInfo](
	[AuditTrailCaseInfoId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[CaseId] [int] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AuditTrailCaseInfo] PRIMARY KEY CLUSTERED 
(
	[AuditTrailCaseInfoId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO



/****** Object:  Table [AuditTrailSearch]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AuditTrailSearch](
	[AuditTrailSearchId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[SearchQuery] [varchar](max) NOT NULL,
	[SearchDisplay] [varchar](max) NOT NULL,
	[SearchUrl] [varchar](max) NOT NULL,
	[AdvancedQuery] [varchar](max) NULL,
	[MRN] [varchar](max) NULL,
	[TotalHits] [int] NOT NULL,
	[ExecutionTime] [decimal](18, 6) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AuditTrailSearch] PRIMARY KEY CLUSTERED 
(
	[AuditTrailSearchId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_AuditTrailSearch_UserId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_AuditTrailSearch_UserId] ON [AuditTrailSearch]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [AuditTrailSearch]  WITH CHECK ADD  CONSTRAINT [FK_AuditTrailSearch_User] FOREIGN KEY([UserId])
REFERENCES [User] ([UserId])
GO
ALTER TABLE [AuditTrailSearch] CHECK CONSTRAINT [FK_AuditTrailSearch_User]
GO



/****** Object:  Table [AuditTrailSearchRequest]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AuditTrailSearchRequest](
	[AuditTrailSearchRequestId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[SearchRequestId] [int] NOT NULL,
	[Action] [varchar](100) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AuditTrailSearchRequest] PRIMARY KEY CLUSTERED 
(
	[AuditTrailSearchRequestId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
