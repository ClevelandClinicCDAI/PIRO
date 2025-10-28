/****** Object:  Table [Cohort]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Cohort](
	[CohortId] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](100) NOT NULL,
	[Description] [varchar](max) NOT NULL,
	[Disease] [varchar](100) NOT NULL,
	[UserId] [int] NOT NULL,
	[IsFacetDisplay] [bit] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[LoadType] [char](1) NOT NULL,
	[IsSolrUpdated] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Cohort] PRIMARY KEY CLUSTERED 
(
	[CohortId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_Cohort_UserId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Cohort_UserId] ON [Cohort]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO


/****** Object:  Table [CohortCase]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CohortCase](
	[CohortCaseId] [int] IDENTITY(1,1) NOT NULL,
	[CohortPatientId] [int] NULL,
	[CohortId] [int] NOT NULL,
	[PatientId] [int] NULL,
	[CaseNumber] [varchar](50) NULL,
	[CaseId] [int] NULL,
	[IsActive] [bit] NOT NULL,
	[LoadType] [char](1) NOT NULL,
	[IsSolrUpdated] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CohortCase] PRIMARY KEY CLUSTERED 
(
	[CohortCaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_CohortCase_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CohortCase_CaseId] ON [CohortCase]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CohortCase_CohortId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CohortCase_CohortId] ON [CohortCase]
(
	[CohortId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CohortCase_PatientId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CohortCase_PatientId] ON [CohortCase]
(
	[PatientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO


/****** Object:  Table [CohortPatient]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CohortPatient](
	[CohortPatientId] [int] IDENTITY(1,1) NOT NULL,
	[CohortId] [int] NOT NULL,
	[PatientId] [int] NULL,
	[PatientMrn] [varchar](100) NULL,
	[PatientEpi] [varchar](50) NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CohortPatient] PRIMARY KEY CLUSTERED 
(
	[CohortPatientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_CohortPatient_CohortId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CohortPatient_CohortId] ON [CohortPatient]
(
	[CohortId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_CohortPatient_PatientId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CohortPatient_PatientId] ON [CohortPatient]
(
	[PatientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO


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



/****** Object:  Table [Patient]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Patient](
	[PatientId] [int] IDENTITY(1,1) NOT NULL,
	[GenderId] [int] NOT NULL,
	[EthnicityId] [int] NOT NULL,
	[RaceId] [int] NOT NULL,
	[MaritalStatusId] [int] NOT NULL,
	[LanguageId] [int] NOT NULL,
	[FirstName] [varchar](256) NOT NULL,
	[LastName] [varchar](256) NOT NULL,
	[MiddleName] [varchar](256) NOT NULL,
	[DOB] [datetime] NOT NULL,
	[MRN] [varchar](100) NOT NULL,
	[PatId] [varchar](100) NOT NULL,
	[EpiId] [varchar](100) NOT NULL,
	[City] [varchar](100) NOT NULL,
	[State] [varchar](100) NOT NULL,
	[Country] [varchar](100) NOT NULL,
	[IsDeceased] [bit] NOT NULL,
	[DeathDate] [datetime] NULL,
	[IsActive] [bit] NOT NULL,
	[RefPatientKey] [varchar](50) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Patient] PRIMARY KEY CLUSTERED 
(
	[PatientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IDX_Patient_MRN]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IDX_Patient_MRN] ON [Patient]
(
	[MRN] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IDX_Patient_RefPatientKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IDX_Patient_RefPatientKey] ON [Patient]
(
	[RefPatientKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [Patient]  WITH CHECK ADD  CONSTRAINT [FK_Patient_Ethnicity] FOREIGN KEY([EthnicityId])
REFERENCES [Ethnicity] ([EthnicityId])
GO
ALTER TABLE [Patient] CHECK CONSTRAINT [FK_Patient_Ethnicity]
GO
ALTER TABLE [Patient]  WITH CHECK ADD  CONSTRAINT [FK_Patient_Gender] FOREIGN KEY([GenderId])
REFERENCES [Gender] ([GenderId])
GO
ALTER TABLE [Patient] CHECK CONSTRAINT [FK_Patient_Gender]
GO
