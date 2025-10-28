/****** Object:  Table [CaseCommentSolr]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseCommentSolr](
	[CaseCommentSolrId] [int] IDENTITY(1,1) NOT NULL,
	[CaseCommentTypeId] [varchar](60) NULL,
	[CaseId] [int] NOT NULL,
	[CommentTypeId] [int] NOT NULL,
	[CommentType] [varchar](100) NOT NULL,
	[CommentCount] [int] NULL,
	[CommentText] [varchar](max) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseCommentSolr] PRIMARY KEY CLUSTERED 
(
	[CaseCommentSolrId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSolr_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSolr_CaseId] ON [CaseCommentSolr]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseCommentSolr_CommentTypeId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseCommentSolr_CommentTypeId] ON [CaseCommentSolr]
(
	[CommentTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [CaseSolr]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseSolr](
	[CaseId] [int] NOT NULL,
	[RefRequisitionKey] [varchar](50) NOT NULL,
	[SpecimenYear] [int] NOT NULL,
	[CaseNumber] [varchar](100) NOT NULL,
	[AccessionDate] [datetime] NULL,
	[ReceiveDate] [datetime] NULL,
	[OverdueDate] [datetime] NULL,
	[CollectionDate] [datetime] NULL,
	[SignoutDate] [datetime] NULL,
	[PatientName] [varchar](768) NULL,
	[PatientDOB] [datetime] NOT NULL,
	[PatientEpi] [varchar](100) NOT NULL,
	[PatientMrn] [varchar](100) NOT NULL,
	[PatientLanguage] [varchar](100) NOT NULL,
	[PatientEthnicity] [varchar](100) NOT NULL,
	[PatientGender] [varchar](100) NOT NULL,
	[PatientDeathDate] [datetime] NULL,
	[PatientIsDeceased] [bit] NOT NULL,
	[PatientRace] [varchar](100) NOT NULL,
	[PatientCity] [varchar](100) NOT NULL,
	[PatientState] [varchar](100) NOT NULL,
	[PatientCountry] [varchar](100) NOT NULL,
	[Hospital] [varchar](100) NOT NULL,
	[Region] [varchar](100) NOT NULL,
	[CaseStatus] [varchar](100) NOT NULL,
	[CaseType] [varchar](100) NOT NULL,
	[CaseTypeCategory] [varchar](100) NOT NULL,
	[ReviewType] [varchar](100) NOT NULL,
	[Specialty] [varchar](100) NOT NULL,
	[SpecialtyCode] [varchar](50) NOT NULL,
	[SpecialtyCategory] [varchar](100) NOT NULL,
	[ADDEND] [varchar](max) NOT NULL,
	[ADDENDCount] [int] NOT NULL,
	[COMMENT] [varchar](max) NOT NULL,
	[COMMENTCount] [int] NOT NULL,
	[FINAL] [varchar](max) NOT NULL,
	[FINALCount] [int] NOT NULL,
	[GROSS] [varchar](max) NOT NULL,
	[GROSSCount] [int] NOT NULL,
	[INTRAOP] [varchar](max) NOT NULL,
	[INTRAOPCount] [int] NOT NULL,
	[RESIDENT] [varchar](max) NOT NULL,
	[RESIDENTCount] [int] NOT NULL,
	[SYNOPTIC] [varchar](max) NOT NULL,
	[SYNOPTICCount] [int] NOT NULL,
	[CLINICAL] [varchar](max) NOT NULL,
	[CLINICALCount] [int] NOT NULL,
	[Interpreter] [varchar](1000) NOT NULL,
	[ProcedureCategory] [varchar](1000) NOT NULL,
	[StaffName] [varchar](8000) NOT NULL,
	[SpecimenNumber] [varchar](8000) NOT NULL,
	[CasePatientAge] [varchar](100) NOT NULL,
	[CasePatientAgeYears] [int] NOT NULL,
	[AnnotationMalignant] [varchar](50) NOT NULL,
	[IsEpic] [bit] NOT NULL,
	[IsEpicMigrated] [bit] NOT NULL,
	[IsCopath] [bit] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[IsSolrUpdate] [bit] NULL,
 CONSTRAINT [PK_CaseSolr] PRIMARY KEY CLUSTERED 
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO



/****** Object:  Table [CaseStaffSolr]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseStaffSolr](
	[CaseStaffSolrId] [int] IDENTITY(1,1) NOT NULL,
	[Pathologist] [varchar](1000) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseStaffSolr] PRIMARY KEY CLUSTERED 
(
	[CaseStaffSolrId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO



