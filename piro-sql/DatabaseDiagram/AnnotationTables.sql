/****** Object:  Table [AnnotationConfigurationData]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AnnotationConfigurationData](
	[AnnotationConfigurationDataId] [int] IDENTITY(1,1) NOT NULL,
	[AnnotationConfigurationId] [int] NOT NULL,
	[FromValue] [varchar](50) NOT NULL,
	[ToValue] [varchar](50) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AnnotationConfigurationData] PRIMARY KEY CLUSTERED 
(
	[AnnotationConfigurationDataId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO



/****** Object:  Table [AnnotationConfiguration]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AnnotationConfiguration](
	[AnnotationConfigurationId] [int] IDENTITY(1,1) NOT NULL,
	[AnnotationMetric] [varchar](50) NOT NULL,
	[DisplayText] [varchar](50) NOT NULL,
	[DataParseProperty] [varchar](50) NOT NULL,
	[UIModel] [varchar](50) NOT NULL,
	[RowIndex] [int] NOT NULL,
	[ColumnIndex] [int] NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AnnotationConfiguration] PRIMARY KEY CLUSTERED 
(
	[AnnotationConfigurationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO




/****** Object:  Table [AnnotationConfigurationData]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AnnotationConfigurationData](
	[AnnotationConfigurationDataId] [int] IDENTITY(1,1) NOT NULL,
	[AnnotationConfigurationId] [int] NOT NULL,
	[FromValue] [varchar](50) NOT NULL,
	[ToValue] [varchar](50) NOT NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK_AnnotationConfigurationData] PRIMARY KEY CLUSTERED 
(
	[AnnotationConfigurationDataId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO




/****** Object:  Table [AnnotationData]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [AnnotationData](
	[AnnotationId] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NULL,
	[ModelName] [varchar](50) NULL,
	[AnnotationValue] [nvarchar](50) NULL,
	[AnnotationKey] [nvarchar](50) NULL,
	[CreateDate] [datetime] NOT NULL,
	[CreateBy] [varchar](100) NOT NULL,
	[UpdateDate] [datetime] NULL,
	[UpdateBy] [varchar](100) NULL,
 CONSTRAINT [PK__Annotati__FC2AC5A37A61F0BD] PRIMARY KEY CLUSTERED 
(
	[AnnotationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AnnotationData_AnnotationKey]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_AnnotationData_AnnotationKey] ON [AnnotationData]
(
	[AnnotationKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_AnnotationData_CaseId]    Script Date: 9/10/2025 4:46:58 PM ******/
CREATE NONCLUSTERED INDEX [IX_AnnotationData_CaseId] ON [AnnotationData]
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



 


/****** Object:  Table [Annotations]    Script Date: 9/10/2025 4:46:58 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Annotations](
	[AnnotationID] [int] IDENTITY(1,1) NOT NULL,
	[CaseId] [int] NULL,
	[AnnotationValue] [nvarchar](50) NULL,
	[AnnotationKey] [nvarchar](50) NULL,
	[DateStamp] [date] NULL,
PRIMARY KEY CLUSTERED 
(
	[AnnotationID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
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
