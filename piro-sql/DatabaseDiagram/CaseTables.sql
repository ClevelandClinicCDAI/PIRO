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








/****** Object:  Table [CaseStaff]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseStaff](
	[CaseStaffId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[StaffId] [int] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[RefRequisitionKey] [varchar](50) NULL,
	[RefEmployeeKey] [varchar](50) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseStaff] PRIMARY KEY CLUSTERED 
(
	[CaseStaffId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseStaff_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseStaff_CaseId] ON [CaseStaff]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_CaseStaff_RefEmployeeKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseStaff_RefEmployeeKey] ON [CaseStaff]
(
	[RefEmployeeKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_CaseStaff_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseStaff_RefRequisitionKey] ON [CaseStaff]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [CaseStaff]  WITH CHECK ADD  CONSTRAINT [FK_CaseStaff_Case] FOREIGN KEY([CaseId])
REFERENCES [Case] ([CaseId])
GO
ALTER TABLE [CaseStaff] CHECK CONSTRAINT [FK_CaseStaff_Case]
GO
ALTER TABLE [CaseStaff]  WITH CHECK ADD  CONSTRAINT [FK_CaseStaff_Staff] FOREIGN KEY([StaffId])
REFERENCES [Staff] ([StaffId])
GO
ALTER TABLE [CaseStaff] CHECK CONSTRAINT [FK_CaseStaff_Staff]
GO









/****** Object:  Table [CaseStatus]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseStatus](
	[CaseStatusId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_CaseStatus] PRIMARY KEY CLUSTERED 
(
	[CaseStatusId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_CaseStatus_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseStatus_DataLabReference] ON [CaseStatus]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO







/****** Object:  Table [CaseType]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseType](
	[CaseTypeId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[CaseTypeCategory] [varchar](100) NOT NULL,
	[ReviewType] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[CaseTypeInfo] [varchar](255) NULL,
	[WorklistTypeInfo] [varchar](255) NULL,
	[DataLabReferenceCategory] [varchar](100) NULL,
 CONSTRAINT [PK_CaseType] PRIMARY KEY CLUSTERED 
(
	[CaseTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_CaseType_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseType_DataLabReference] ON [CaseType]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO








/****** Object:  Table [CaseAnnotation]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [CaseAnnotation](
	[CaseAnnotationId] [int] IDENTITY(1,1) NOT NULL,
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
 CONSTRAINT [PK_CaseAnnotation] PRIMARY KEY CLUSTERED 
(
	[CaseAnnotationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_CaseAnnotation_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_CaseAnnotation_CaseId] ON [CaseAnnotation]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO






/****** Object:  Table [Ethnicity]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Ethnicity](
	[EthnicityId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Ethnicity] PRIMARY KEY CLUSTERED 
(
	[EthnicityId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Ethnicity_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Ethnicity_DataLabReference] ON [Ethnicity]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO





/****** Object:  Table [Gender]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Gender](
	[GenderId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Gender] PRIMARY KEY CLUSTERED 
(
	[GenderId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Gender_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Gender_DataLabReference] ON [Gender]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [Hospital]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Hospital](
	[HospitalId] [int] IDENTITY(1,1) NOT NULL,
	[RegionId] [int] NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Hospital] PRIMARY KEY CLUSTERED 
(
	[HospitalId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Hospital_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Hospital_DataLabReference] ON [Hospital]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [Interpreter]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Interpreter](
	[InterpreterId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[ProcedureDescription] [varchar](1000) NULL,
	[ProcedureCategoryDescription] [varchar](1000) NULL,
	[FullName] [varchar](1000) NULL,
	[RefRequisitionKey] [varchar](100) NULL,
	[RefOrdKey] [varchar](100) NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[ProcedureType] [varchar](1000) NULL,
	[RefOrdId] [decimal](38, 0) NULL,
	[RefRequisitionId] [decimal](38, 0) NULL,
 CONSTRAINT [PK_Interpreter] PRIMARY KEY CLUSTERED 
(
	[InterpreterId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_Interpreter_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Interpreter_CaseId] ON [Interpreter]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Interpreter_RefOrdKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Interpreter_RefOrdKey] ON [Interpreter]
(
	[RefOrdKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Interpreter_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Interpreter_RefRequisitionKey] ON [Interpreter]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO






/****** Object:  Table [Language]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Language](
	[LanguageId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Language] PRIMARY KEY CLUSTERED 
(
	[LanguageId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Language_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Language_DataLabReference] ON [Language]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [LinkedOrder]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [LinkedOrder](
	[LinkedOrderId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NULL,
	[ComponentName] [varchar](1000) NULL,
	[ComponentExternalName] [varchar](1000) NULL,
	[ProcedureDesc] [varchar](1000) NULL,
	[DefaultUnit] [varchar](1000) NULL,
	[OrdValue] [varchar](1000) NULL,
	[OrdNumValue] [decimal](38, 5) NULL,
	[OrdLow] [varchar](1000) NULL,
	[OrdHigh] [varchar](1000) NULL,
	[OrdUnit] [varchar](1000) NULL,
	[OrdRawValue] [varchar](1000) NULL,
	[OrdRawHigh] [varchar](1000) NULL,
	[OrdRawLow] [varchar](1000) NULL,
	[ResultDate] [datetime] NULL,
	[OrderDate] [datetime] NULL,
	[ReviewDate] [datetime] NULL,
	[RefRequisitionId] [decimal](38, 0) NULL,
	[RefSpecTestOrderId] [decimal](38, 0) NULL,
	[RefOrderId] [decimal](38, 0) NULL,
	[RefOrderProcId] [decimal](38, 0) NULL,
	[RefComponentId] [decimal](38, 0) NULL,
	[RefProcId] [decimal](38, 0) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL
) ON [PRIMARY]
GO
/****** Object:  Index [IX_LinkedOrder_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_LinkedOrder_CaseId] ON [LinkedOrder]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO




/****** Object:  Table [MaritalStatus]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [MaritalStatus](
	[MaritalStatusId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_MaritalStatus] PRIMARY KEY CLUSTERED 
(
	[MaritalStatusId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_MaritalStatus_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_MaritalStatus_DataLabReference] ON [MaritalStatus]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
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






/****** Object:  Table [Race]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Race](
	[RaceId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](50) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Race] PRIMARY KEY CLUSTERED 
(
	[RaceId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Race_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Race_DataLabReference] ON [Race]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO






/****** Object:  Table [Region]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Region](
	[RegionId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Region] PRIMARY KEY CLUSTERED 
(
	[RegionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Region_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Region_DataLabReference] ON [Region]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO




/****** Object:  Table [Specialty]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Specialty](
	[SpecialtyId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[SpecialtyCategory] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Speciality] PRIMARY KEY CLUSTERED 
(
	[SpecialtyId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Speciality_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Speciality_DataLabReference] ON [Specialty]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [Specimen]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Specimen](
	[SpecimenId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NOT NULL,
	[PatientId] [int] NOT NULL,
	[SpecimenStatusId] [int] NOT NULL,
	[SpecimenDrawTypeId] [int] NOT NULL,
	[SpecimenSourceId] [int] NOT NULL,
	[SpecimenNumber] [varchar](100) NOT NULL,
	[CollectionDate] [datetime] NULL,
	[ReceivedDate] [datetime] NULL,
	[ClosedDate] [datetime] NULL,
	[IsReceivedByBarcode] [bit] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[RefRequisitionKey] [decimal](38, 0) NOT NULL,
	[RefSpecimenKey] [varchar](50) NOT NULL,
	[RefPatientKey] [varchar](50) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Specimen] PRIMARY KEY CLUSTERED 
(
	[SpecimenId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_Specimen_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Specimen_CaseId] ON [Specimen]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Specimen_RefPaitentKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Specimen_RefPaitentKey] ON [Specimen]
(
	[RefPatientKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Specimen_RefRequisitionKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Specimen_RefRequisitionKey] ON [Specimen]
(
	[RefRequisitionKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Specimen_RefSpecimenKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Specimen_RefSpecimenKey] ON [Specimen]
(
	[RefSpecimenKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [Specimen]  WITH NOCHECK ADD  CONSTRAINT [FK_Specimen_Case] FOREIGN KEY([CaseId])
REFERENCES [Case] ([CaseId])
GO
ALTER TABLE [Specimen] NOCHECK CONSTRAINT [FK_Specimen_Case]
GO
ALTER TABLE [Specimen]  WITH NOCHECK ADD  CONSTRAINT [FK_Specimen_SpecimenSource] FOREIGN KEY([SpecimenSourceId])
REFERENCES [SpecimenSource] ([SpecimenSourceId])
GO
ALTER TABLE [Specimen] NOCHECK CONSTRAINT [FK_Specimen_SpecimenSource]
GO




/****** Object:  Table [SpecimenDrawType]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [SpecimenDrawType](
	[SpecimenDrawTypeId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SpecimenDrawType] PRIMARY KEY CLUSTERED 
(
	[SpecimenDrawTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_SpecimenDrawType_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_SpecimenDrawType_DataLabReference] ON [SpecimenDrawType]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO




/****** Object:  Table [SpecimenSource]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [SpecimenSource](
	[SpecimenSourceId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](100) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[RCPScore] [decimal](18, 2) NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
	[RCP_ALT] [int] NULL,
 CONSTRAINT [PK_SpecimenSource] PRIMARY KEY CLUSTERED 
(
	[SpecimenSourceId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_SpecimenSource_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_SpecimenSource_DataLabReference] ON [SpecimenSource]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO






/****** Object:  Table [SpecimenStatus]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [SpecimenStatus](
	[SpecimenStatusId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SpecimenStatus] PRIMARY KEY CLUSTERED 
(
	[SpecimenStatusId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_SpecimenStatus_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_SpecimenStatus_DataLabReference] ON [SpecimenStatus]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO





/****** Object:  Table [SpecimenType]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [SpecimenType](
	[SpecimenTypeId] [int] IDENTITY(1,1) NOT NULL,
	[ShortName] [varchar](100) NOT NULL,
	[Code] [varchar](50) NOT NULL,
	[DESCRIPTION] [varchar](1000) NOT NULL,
	[DataLabReference] [varchar](100) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_SpecimenType] PRIMARY KEY CLUSTERED 
(
	[SpecimenTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_SpecimenType_DataLabReference]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_SpecimenType_DataLabReference] ON [SpecimenType]
(
	[DataLabReference] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO




/****** Object:  Table [Staff]    Script Date: 9/10/2025 4:46:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Staff](
	[StaffId] [int] IDENTITY(1,1) NOT NULL,
	[FullName] [varchar](100) NOT NULL,
	[UserId] [varchar](100) NULL,
	[StartDate] [datetime] NULL,
	[EndDate] [datetime] NULL,
	[RefEmployeeKey] [varchar](50) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Staff] PRIMARY KEY CLUSTERED 
(
	[StaffId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Staff_RefEmployeeKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_Staff_RefEmployeeKey] ON [Staff]
(
	[RefEmployeeKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



/****** Object:  Table [Tag]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Tag](
	[TagId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[Name] [varchar](100) NOT NULL,
	[Description] [varchar](max) NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_Tag] PRIMARY KEY CLUSTERED 
(
	[TagId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO




/****** Object:  Table [TagCase]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [TagCase](
	[TagCaseId] [int] IDENTITY(1,1) NOT NULL,
	[TagId] [int] NOT NULL,
	[CaseId] [int] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_TagCase] PRIMARY KEY CLUSTERED 
(
	[TagCaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [TagCase]  WITH CHECK ADD  CONSTRAINT [FK_TagCase_Tag] FOREIGN KEY([TagId])
REFERENCES [Tag] ([TagId])
GO
ALTER TABLE [TagCase] CHECK CONSTRAINT [FK_TagCase_Tag]
GO




