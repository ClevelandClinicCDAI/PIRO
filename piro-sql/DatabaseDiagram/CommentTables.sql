/****** Object:  Table [Case]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Case](
	[CaseId] [int] IDENTITY(1,1) NOT NULL,
	[PatientId] [int] NOT NULL,
	[HospitalId] [int] NOT NULL,
	[CaseStatusId] [int] NOT NULL,
	[CaseTypeId] [int] NOT NULL,
	[SpecialtyId] [int] NOT NULL,
	[SpecimenYear] [int] NOT NULL,
	[CaseNumber] [varchar](100) NOT NULL,
	[AccessionDate] [datetime] NULL,
	[ReceiveDate] [datetime] NULL,
	[OverdueDate] [datetime] NULL,
	[CollectionDate] [datetime] NULL,
	[SignoutDate] [datetime] NULL,
	[RefRequisitionKey] [varchar](50) NOT NULL,
	[RefRequisitionId] [decimal](38, 0) NOT NULL,
	[RefPatientKey] [varchar](50) NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[UploadDate] [datetime] NULL,
 CONSTRAINT [PK_Case] PRIMARY KEY CLUSTERED 
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Case_CaseNumber]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_CaseNumber] ON [Case]
(
	[CaseNumber] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Case_CollectionDate]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_CollectionDate] ON [Case]
(
	[CollectionDate] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Case_RefPatientKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_RefPatientKey] ON [Case]
(
	[RefPatientKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Case_RefRequisitionId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_RefRequisitionId] ON [Case]
(
	[RefRequisitionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Case_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_RefRequisitionKey] ON [Case]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Case_SpecimenYear]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_SpecimenYear] ON [Case]
(
	[SpecimenYear] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Case_UploadDate]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Case_UploadDate] ON [Case]
(
	[UploadDate] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [Case]  WITH CHECK ADD  CONSTRAINT [FK_Case_Hospital] FOREIGN KEY([HospitalId])
REFERENCES [Hospital] ([HospitalId])
GO
ALTER TABLE [Case] CHECK CONSTRAINT [FK_Case_Hospital]
GO
ALTER TABLE [Case]  WITH CHECK ADD  CONSTRAINT [FK_Case_Patient] FOREIGN KEY([PatientId])
REFERENCES [Patient] ([PatientId])
GO
ALTER TABLE [Case] CHECK CONSTRAINT [FK_Case_Patient]
GO

 


/****** Object:  Table [CaseCommentCoPath]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentCoPath](
	[CaseCommentCoPathId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[CommentTypeId] [int] NOT NULL,
	[Text] [varchar](max) NULL,
	[RtfText] [varchar](max) NULL,
	[StatusDate] [datetime] NULL,
	[SpecYear] [int] NULL,
	[RefId] [int] NOT NULL,
	[RefSpecimenId] [varchar](50) NOT NULL,
	[RefCaseNum] [varchar](100) NOT NULL,
	[RefSpecimenNum] [varchar](100) NOT NULL,
	[RefTextType] [varchar](100) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[IsTextUpdated] [bit] NULL,
 CONSTRAINT [PK_CaseCommentCoPath] PRIMARY KEY CLUSTERED 
(
	[CaseCommentCoPathId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [idx_CaseCommentCoPath_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentCoPath_CaseId] ON [CaseCommentCoPath]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [idx_CaseCommentCoPath_CaseNum]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentCoPath_CaseNum] ON [CaseCommentCoPath]
(
	[RefCaseNum] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [idx_CaseCommentCoPath_RefId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentCoPath_RefId] ON [CaseCommentCoPath]
(
	[RefId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseCommentEpic]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentEpic](
	[CaseCommentCoEpicId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[CommentTypeId] [int] NOT NULL,
	[Text] [varchar](max) NOT NULL,
	[NumberOfLines] [int] NOT NULL,
	[RefRequisitionKey] [varchar](50) NOT NULL,
	[RefOrdKey] [varchar](50) NOT NULL,
	[RefLabCompName] [varchar](100) NOT NULL,
	[RefOrdResultDate] [varchar](100) NOT NULL,
	[RefContactDate] [decimal](18, 2) NOT NULL,
	[RefRecNum] [varchar](100) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseCommentEpic] PRIMARY KEY CLUSTERED 
(
	[CaseCommentCoEpicId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [idx_CaseCommentEpic_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentEpic_CaseId] ON [CaseCommentEpic]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [idx_CaseCommentEpic_RefLabCompName]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentEpic_RefLabCompName] ON [CaseCommentEpic]
(
	[RefLabCompName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [idx_CaseCommentEpic_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentEpic_RefRequisitionKey] ON [CaseCommentEpic]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO


/****** Object:  Table [CaseCommentSourceInfo]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSourceInfo](
	[CaseCommentSourceInfoId] [int] IDENTITY(1,1) NOT NULL,
	[RefRequisitionKey] [varchar](50) NOT NULL,
	[CaseId] [int] NOT NULL,
	[CaseNumber] [varchar](100) NOT NULL,
	[IsEpic] [bit] NOT NULL,
	[IsCopath] [bit] NOT NULL,
	[IsEpicMigrated] [bit] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseCommentSourceInfo] PRIMARY KEY CLUSTERED 
(
	[CaseCommentSourceInfoId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [idx_CaseCommentSourceInfo_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentSourceInfo_CaseId] ON [CaseCommentSourceInfo]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [idx_CaseCommentSourceInfo_CaseNumber]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentSourceInfo_CaseNumber] ON [CaseCommentSourceInfo]
(
	[CaseNumber] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [idx_CaseCommentSourceInfo_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [idx_CaseCommentSourceInfo_RefRequisitionKey] ON [CaseCommentSourceInfo]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseCommentSynopticSpecimen]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSynopticSpecimen](
	[Id] [bigint] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[SpecimenId] [int] NOT NULL,
	[SynopticId] [decimal](38, 0) NOT NULL,
	[SynopticLine] [int] NOT NULL,
	[CaseNum] [varchar](254) NOT NULL,
	[SpecimenNum] [varchar](254) NOT NULL,
	[SpecimenList] [varchar](254) NULL,
	[RecordCreateDate] [datetime] NULL,
	[IsSpecimenLevel] [bit] NULL,
	[RefSpecimenKey] [varchar](50) NOT NULL,
	[RefRequisitionKey] [varchar](50) NOT NULL,
	[IsParsed] [bit] NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SynopticCase] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticSpecimen_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticSpecimen_CaseId] ON [CaseCommentSynopticSpecimen]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticSpecimen_SpecimenId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticSpecimen_SpecimenId] ON [CaseCommentSynopticSpecimen]
(
	[SpecimenId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticSpecimen_SynopticId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticSpecimen_SynopticId] ON [CaseCommentSynopticSpecimen]
(
	[SynopticId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseCommentSynopticText]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSynopticText](
	[Id] [bigint] IDENTITY(1,1) NOT NULL,
	[SynopticId] [decimal](38, 0) NOT NULL,
	[Name] [varchar](200) NOT NULL,
	[ResultId] [varchar](50) NOT NULL,
	[HlvId] [decimal](38, 0) NOT NULL,
	[DataType] [varchar](256) NOT NULL,
	[ContextName] [varchar](256) NOT NULL,
	[ContexHierarchy] [varchar](max) NOT NULL,
	[ValueLine] [varchar](50) NOT NULL,
	[Level1] [varchar](1000) NOT NULL,
	[Level2] [varchar](1000) NOT NULL,
	[Level3] [varchar](1000) NOT NULL,
	[Level4] [varchar](1000) NOT NULL,
	[Level5] [varchar](1000) NOT NULL,
	[Level6] [varchar](1000) NOT NULL,
	[ElementName] [varchar](256) NOT NULL,
	[ElementValue] [varchar](max) NOT NULL,
	[SynopticKey] [varchar](50) NOT NULL,
	[ElementComment] [varchar](max) NOT NULL,
	[CommentLine] [varchar](50) NOT NULL,
	[CommentSequence] [int] NOT NULL,
	[RefSynopticKey] [varchar](50) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SynopticText] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticText_HlvId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticText_HlvId] ON [CaseCommentSynopticText]
(
	[HlvId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticText_SynopticId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticText_SynopticId] ON [CaseCommentSynopticText]
(
	[SynopticId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseCommentSynopticTextComment]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSynopticTextComment](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[SynopticId] [decimal](38, 0) NULL,
	[HlvId] [decimal](38, 0) NOT NULL,
	[Line] [int] NULL,
	[Comment] [varchar](max) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseCommentSynopticTextComment] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticTextComment_HlvId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticTextComment_HlvId] ON [CaseCommentSynopticTextComment]
(
	[HlvId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSynopticTextComment_SynopticId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSynopticTextComment_SynopticId] ON [CaseCommentSynopticTextComment]
(
	[SynopticId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseCommentSynopticReportData]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSynopticReportData](
	[SynopticId] [int] NULL,
	[CaseId] [int] NULL,
	[CaseNumber] [varchar](1000) NULL,
	[Level] [int] NULL,
	[Key] [varchar](1000) NULL,
	[Value] [varchar](1000) NULL,
	[TextId] [int] NULL,
	[CommentId] [int] NULL,
	[Level1] [varchar](1000) NULL,
	[Level2] [varchar](1000) NULL,
	[Level3] [varchar](1000) NULL,
	[Level4] [varchar](1000) NULL,
	[Level5] [varchar](1000) NULL,
	[Level16] [varchar](1000) NULL,
	[ElementValue] [varchar](1000) NULL,
	[Comment] [varchar](1000) NULL,
	[CommentSequence] [int] NULL,
	[NewCommentSequence] [decimal](18, 4) NULL
) ON [PRIMARY]
GO



/****** Object:  Table [CaseComment]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseComment](
	[CaseCommentId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[CommentTypeId] [int] NOT NULL,
	[Text] [varchar](max) NOT NULL,
	[RefRequistionKey] [decimal](38, 0) NOT NULL,
	[RefResultKey] [decimal](38, 0) NOT NULL,
	[RefLabCompName] [varchar](100) NOT NULL,
	[RefCommentType] [varchar](100) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[RefComponentDate] [datetime] NULL,
 CONSTRAINT [PK_CaseComment] PRIMARY KEY CLUSTERED 
(
	[CaseCommentId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseComment_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseComment_CaseId] ON [CaseComment]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseComment_CaseId_CommentTypeId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseComment_CaseId_CommentTypeId] ON [CaseComment]
(
	[CaseId] ASC,
	[CommentTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseComment_CreateDate]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseComment_CreateDate] ON [CaseComment]
(
	[CreateDate] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [CaseComment]  WITH CHECK ADD  CONSTRAINT [FK_CaseComment_Case] FOREIGN KEY([CaseId])
REFERENCES [Case] ([CaseId])
GO
ALTER TABLE [CaseComment] CHECK CONSTRAINT [FK_CaseComment_Case]
GO
ALTER TABLE [CaseComment]  WITH CHECK ADD  CONSTRAINT [FK_CaseComment_CommentType] FOREIGN KEY([CommentTypeId])
REFERENCES [CommentType] ([CommentTypeId])
GO
ALTER TABLE [CaseComment] CHECK CONSTRAINT [FK_CaseComment_CommentType]
GO
