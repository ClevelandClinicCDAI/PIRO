IF OBJECT_ID(N'dbo.sysssislog', N'U') IS NOT NULL
BEGIN
    EXEC sp_rename 'sysssislog', 'SSIS_LogSystem';
END
GO

 CREATE OR ALTER PROCEDURE [dbo].[sp_ssis_addlogentry]  @event sysname,  @computer nvarchar(128),  @operator nvarchar(128),  @source nvarchar(1024), 
 @sourceid uniqueidentifier,  @executionid uniqueidentifier,  @starttime datetime,  @endtime datetime,  
 @datacode int,  @databytes image,  @message nvarchar(2048)
 AS  
 BEGIN
	 INSERT INTO dbo.SSIS_LogSystem (      event,      computer,      operator,      source,      sourceid,      executionid,      starttime,      endtime,     
	 datacode,      databytes,      message )  VALUES (      @event,      @computer,      @operator,      @source,      @sourceid,      @executionid,      
	 @starttime,      @endtime,      @datacode,      @databytes,      @message )  RETURN 0
 END
GO
IF OBJECT_ID(N'dbo.SSIS_LogCustom', N'U') IS NOT NULL
BEGIN
    Drop Table dbo.SSIS_LogCustom
END

CREATE TABLE [dbo].[SSIS_LogCustom](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[MachineName] [varchar](500) NULL,
	[PackageName] [varchar](500) NULL,
	[SourceId] [varchar](500) NULL,
	[SourceName] [varchar](500) NULL,
	[TaskName] [varchar](500) NULL,
	[Message] [varchar](Max) NULL,
	[CreateDate] [datetime] NULL,
 CONSTRAINT [PK_SSIS_LogCustom] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
 GO


 
IF OBJECT_ID(N'dbo.SSIS_LogSystem', N'U') IS NOT NULL
BEGIN
    Drop Table dbo.SSIS_LogSystem
END
CREATE TABLE [dbo].[SSIS_LogSystem](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[event] [sysname] NOT NULL,
	[computer] [nvarchar](128) NOT NULL,
	[operator] [nvarchar](128) NOT NULL,
	[source] [nvarchar](1024) NOT NULL,
	[sourceid] [uniqueidentifier] NOT NULL,
	[executionid] [uniqueidentifier] NOT NULL,
	[starttime] [datetime] NOT NULL,
	[endtime] [datetime] NOT NULL,
	[datacode] [int] NOT NULL,
	[databytes] [image] NULL,
	[message] [nvarchar](2048) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


 
IF OBJECT_ID(N'dbo.SSIS_CaseData', N'U') IS NOT NULL
BEGIN
    Drop Table dbo.SSIS_CaseData
END
 

CREATE TABLE [dbo].[SSIS_CaseData](
	[CASE_ID] [bigint] NOT NULL,
	[CASE_ACCESSION_DTTM] [datetime] NULL,
	[CASE_RECEIVED_DTTM] [datetime] NULL,
	[CASE_OVERDUE_DTTM] [datetime] NULL,
	[CASE_PAT_ID] [varchar](18) NULL,
	[CASE_LAB_ID] [varchar](18) NULL,
	[CASE_COLL_DTTM] [datetime] NULL,
	[CASE_SIGNOUT_DTTM] [datetime] NULL,
	[CASE_TASK_ADD_DTTM] [datetime] NULL,
	[INSTANT_PAT_ASSOC_UTC_DTTM] [datetime] NULL,
	[CASE_SUBSPECIALTY_C] [decimal](38, 0) NULL,
	[PAT_ASSOC_DTTM] [datetime] NULL,
	[CASE_TYPE_ID] [varchar](18) NULL,
	[CASE_NUM] [varchar](254) NULL,
	[AP_CASE_STATUS_C] [decimal](38, 0) NULL,
	[LAST_TASK_ADDED_UTC_DTTM] [datetime] NULL,
	[CASE_ACCESSION_UTC_DTTM] [datetime] NULL,
	 CONSTRAINT [PK_SSIS_CaseData] PRIMARY KEY CLUSTERED 
	(
		[CASE_ID] ASC
	))
	GO
 

 


 
/****** Object:  Table [dbo].[SSIS_ConfigPackage]    Script Date: 4/1/2025 5:03:22 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SSIS_ConfigPackage]') AND type in (N'U'))
DROP TABLE [dbo].[SSIS_ConfigPackage]
 

CREATE TABLE [dbo].[SSIS_ConfigPackage](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[PackageFolderPath] [varchar](500) NOT NULL,
	[PackageFileName] [varchar](500) NOT NULL,
	[Sequence] [int] NOT NULL,
	[IsActive] [bit] NOT NULL,
 CONSTRAINT [PK_SsisConfigPackage] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


/****** Object:  Table [dbo].[SSIS_ConfigRun]    Script Date: 4/1/2025 5:03:51 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SSIS_ConfigRun]') AND type in (N'U'))
DROP TABLE [dbo].[SSIS_ConfigRun]
 
CREATE TABLE [dbo].[SSIS_ConfigRun](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](1000) NOT NULL,
	[Val] [varchar](4000) NOT NULL,
	IsActive bit NOT NULL,
 CONSTRAINT [PK_SSISConfig] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

Truncate Table [dbo].[SSIS_ConfigRun]
Insert into [dbo].[SSIS_ConfigRun]
Values ('LastRunDate', cast(getdate() as date), 1)
--Insert into [dbo].[SSIS_ConfigRun]
--Values ('FromDate', '1900-01-01', 1)
--Insert into [dbo].[SSIS_ConfigRun]
--Values ('ToDate', '2000-01-01', 1)
--Insert into [dbo].[SSIS_ConfigRun]
--Values ('MAXRows', '1', 1)

Insert into [dbo].[SSIS_ConfigRun]
Values ('FromDate', '', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('ToDate', '', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('MAXRows', '', 1)


Update [dbo].[SSIS_ConfigRun] set Val = '2020-01-01' Where [NAME] = 'LastRunDate'
Insert into [dbo].[SSIS_ConfigRun]
Values ('ResultIdStart', '1', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('ResultIdEnd', '4000000000', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_SpecimenSource', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_SpecimenDrawType', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_SpecimenStatus', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CaseType', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CaseTypeCategory', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_PatientRace', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CaseStatus', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_MatrialStatus', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_Language', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_Gender', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CaseFlag', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_EthnicGroup', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_SpecimenType', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_Lab', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_Specimen', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CaseData', 1)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CommentSynopticSpecimenLevel', 0)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CommentSynopticCaseLevel', 0)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CommentSynopticText', 0)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CommentPlainText', 0)
Insert into [dbo].[SSIS_ConfigRun]
Values ('Truncate.OnLoad', 'SSIS_CommentRTFText', 0)
Insert into [dbo].[SSIS_ConfigRun]
Values (
	'Query.CommentPlainText.CommentType.CategorizationClause',
	'CASE WHEN COMP.NAME LIKE ''%FINAL PERFORMING LAB%'' THEN ''OTHER'' WHEN COMP.NAME LIKE ''%FINALPERFORMINGLAB%'' THEN ''OTHER'' WHEN COMP.NAME LIKE ''%FINAL%'' THEN ''FINAL'' WHEN COMP.NAME LIKE ''%GROSS%'' THEN ''GROSS'' WHEN COMP.NAME LIKE ''%INTRAOP%'' THEN ''INTRAOP'' WHEN COMP.NAME LIKE ''%COMMENT%'' THEN ''COMMENT'' WHEN COMP.NAME LIKE ''%SYNOPTIC%'' THEN ''SYNOPTIC'' WHEN COMP.NAME LIKE ''%RESIDENT%'' THEN ''RESIDENT'' WHEN COMP.NAME LIKE ''%ADDEND%'' THEN ''ADDEND'' WHEN COMP.NAME LIKE ''%MICROSCOPIC%'' THEN ''MICROSCOPIC'' WHEN COMP.NAME LIKE ''FLOW CYTOMETRY RESULTS'' THEN ''FINAL'' ELSE ''OTHER'' END',
	1
)
 

IF OBJECT_ID(N'dbo.SSIS_SpecimenSource', N'U') IS NOT NULL
BEGIN
    Drop Table dbo.SSIS_SpecimenSource
END


CREATE TABLE [dbo].[SSIS_SpecimenSource] 
   (	[SPECIMEN_SOURCE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_SpecimenSource] PRIMARY KEY ([SPECIMEN_SOURCE_C])
   )
   GO



IF OBJECT_ID(N'dbo.SSIS_SpecimenDrawType', N'U') IS NOT NULL
BEGIN
    Drop Table dbo.SSIS_SpecimenDrawType
END

CREATE TABLE [dbo].[SSIS_SpecimenDrawType] 
   (	[SPEC_DRAW_TYPE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_SpecimenDrawType] PRIMARY KEY ([SPEC_DRAW_TYPE_C])
   ) 
   GO

IF OBJECT_ID(N'dbo.SSIS_SpecimenStatus', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_SpecimenStatus
END

CREATE TABLE [dbo].[SSIS_SpecimenStatus] 
   (	[SPEC_VAL_STAT_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_SpecimenStatus] PRIMARY KEY ([SPEC_VAL_STAT_C])
   ) 
   
   GO


   IF OBJECT_ID(N'dbo.SSIS_CaseType', N'U') IS NOT NULL
	BEGIN
		Drop Table dbo.SSIS_CaseType
	END

    CREATE TABLE [dbo].[SSIS_CaseType] 
   (	[LAB_ID] VARCHAR(18) NOT NULL, 
	[CM_PHY_OWNER_ID] VARCHAR(25) , 
	[CM_LOG_OWNER_ID] VARCHAR(25) , 
	[ID_PIECE_FORMAT_C] DECIMAL(38,0), 
	[DELIM_PREC_SLD] VARCHAR(10) , 
	[DELIM_PREC_SPEC] VARCHAR(10) , 
	[AP_WORKLIST_TYPE_C] DECIMAL(38,0), 
	[CASE_TYPE_NAME] VARCHAR(254) , 
	[AP_USE_HISTOLOGY_YN] VARCHAR(1) , 
	[CASE_EXPECTED_LEN] DECIMAL(38,0), 
	[CASE_EXPECTED_LEN_C] DECIMAL(38,0), 
	[TYPE_CASE_C] DECIMAL(38,0), 
	[AP_REL_RPT_SET_ID] BIGINT, 
	[AP_USE_IN_BASKET_YN] VARCHAR(1) , 
	[REPORT_NAME] VARCHAR(254) , 
	[AP_QA_RPT_SET_ID] BIGINT, 
	[MED_CYTO_WORKFLOW_C] DECIMAL(38,0), 
	[AP_CHRG_REVIEW_YN] VARCHAR(1) , 
	[SKIP_ON_SOURCE_YN] VARCHAR(1) , 
	[ALLOW_MANUAL_NUM_C] DECIMAL(38,0), 
	[AP_CHRG_REVIEW_C] DECIMAL(38,0), 
	[BELONGS_TO_LAB_ID] VARCHAR(18) 
   ) 
   ALTER TABLE[dbo].[SSIS_CaseType]  ADD CONSTRAINT [PK_SSIS_CaseType] PRIMARY KEY ([LAB_ID])
GO

 IF OBJECT_ID(N'dbo.SSIS_CaseTypeCategory', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CaseTypeCategory
END

CREATE TABLE [dbo].[SSIS_CaseTypeCategory] 
(	[TYPE_CASE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	CONSTRAINT [PK_SSIS_CaseTypeCategory] PRIMARY KEY ([TYPE_CASE_C])
)  
   GO

 IF OBJECT_ID(N'dbo.SSIS_PatientRace', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_PatientRace
END

CREATE TABLE [dbo].[SSIS_PatientRace] 
   (	[PATIENT_RACE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_PatientRace] PRIMARY KEY ([PATIENT_RACE_C])
   ) 
GO

 IF OBJECT_ID(N'dbo.SSIS_CaseStatus', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CaseStatus
END
CREATE TABLE [dbo].[SSIS_CaseStatus] 
   (	[AP_CASE_STATUS_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_CaseStatus] PRIMARY KEY ([AP_CASE_STATUS_C])
   ) 
GO

 IF OBJECT_ID(N'dbo.SSIS_MatrialStatus', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_MatrialStatus
END
CREATE TABLE [dbo].[SSIS_MatrialStatus] 
   (	[MARITAL_STATUS_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_MatrialStatus] PRIMARY KEY ([MARITAL_STATUS_C])
   )
GO

IF OBJECT_ID(N'dbo.SSIS_Language', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_Language
END
CREATE TABLE [dbo].[SSIS_Language] 
   (	[LANGUAGE_C] VARCHAR(66) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] VARCHAR(66) , 
	 CONSTRAINT [PK_SSIS_Language] PRIMARY KEY ([LANGUAGE_C])
   )  
GO



IF OBJECT_ID(N'dbo.SSIS_Gender', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_Gender
END
CREATE TABLE [dbo].[SSIS_Gender] 
   (	[GENDER_CODE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_Gender] PRIMARY KEY ([GENDER_CODE_C])
   ) 
   GO

IF OBJECT_ID(N'dbo.SSIS_CaseFlag', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CaseFlag
END
CREATE TABLE [dbo].[SSIS_CaseFlag] 
   (	[CASE_FLAGS_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_CaseFlag] PRIMARY KEY ([CASE_FLAGS_C])
   )
   GO

IF OBJECT_ID(N'dbo.SSIS_EthnicGroup', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_EthnicGroup
END
	CREATE TABLE [dbo].[SSIS_EthnicGroup] 
   (	[ETHNIC_GROUP_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_EthnicGroup] PRIMARY KEY ([ETHNIC_GROUP_C])
   )
   GO


   IF OBJECT_ID(N'dbo.SSIS_SpecimenType', N'U') IS NOT NULL
	BEGIN
		Drop Table dbo.SSIS_SpecimenType
	END
   CREATE TABLE [dbo].[SSIS_SpecimenType] 
   (	[SPECIMEN_TYPE_C] DECIMAL(38,0) NOT NULL, 
	[NAME] VARCHAR(254) , 
	[TITLE] VARCHAR(254) , 
	[ABBR] VARCHAR(254) , 
	[INTERNAL_ID] DECIMAL(38,0), 
	 CONSTRAINT [PK_SSIS_SpecimenType] PRIMARY KEY ([SPECIMEN_TYPE_C])
   ) 
   GO



   IF OBJECT_ID(N'dbo.SSIS_Lab', N'U') IS NOT NULL
	BEGIN
		Drop Table dbo.SSIS_Lab
	END
   CREATE TABLE [dbo].[SSIS_Lab] 
   (	[LAB_ID] VARCHAR(18) NOT NULL, 
	[CM_PHY_OWNER_ID] VARCHAR(25) , 
	[CM_LOG_OWNER_ID] VARCHAR(25) , 
	[LAB_NAME] VARCHAR(200) , 
	[STATUS_C] DECIMAL(38,0), 
	[LIVE_STATUS_C] DECIMAL(38,0), 
	[RECORD_DELETED_C] DECIMAL(38,0)
   )
   
   ALTER TABLE [dbo].[SSIS_Lab] ADD CONSTRAINT [PK_SSIS_Lab] PRIMARY KEY ([LAB_ID])
   GO

IF OBJECT_ID(N'dbo.SSIS_Specimen', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_Specimen
END 

CREATE TABLE [dbo].[SSIS_Specimen](
	[SPECIMEN_ID] [varchar](18) NOT NULL,
	[LAB_ID] [varchar](18) NULL,
	[SPEC_NUMBER_LN1] [varchar](254) NULL,
	[SPEC_DTM_COLLECTED] [datetime] NULL,
	[SPEC_DTM_RECEIVED] [datetime] NULL,
	[SPEC_SOURCE_C] [decimal](38, 0) NULL,
	[SPEC_COLLECT_BY] [varchar](254) NULL,
	[SPEC_EPT_PAT_ID] [varchar](18) NULL,
	[SPEC_QC_FLAG_YN] [varchar](254) NULL,
	[SPEC_VAL_STAT_C] [decimal](38, 0) NULL,
	[SPEC_CLOSED_DT] [datetime] NULL,
	[SPEC_COLL_BY_ID] [varchar](18) NULL,
	[SPEC_DRAW_TYPE_C] [decimal](38, 0) NULL,
	[CASE_ID] [bigint] NULL,
	[SPEC_DELETED_YN] [varchar](1) NULL,
	[SPEC_COLL_UTC_DTTM] [datetime] NULL,
	[SPEC_RCVD_UTC_DTTM] [datetime] NULL,
	[SPEC_FROZEN_YN] [varchar](1) NULL,
	[AP_RECEIVE_UTC_DTTM] [datetime] NULL,
	[AP_RECEIVED_BY_ID] [varchar](18) NULL,
	[RECV_BY_BARCODE_YN] [varchar](1) NULL,
	[SPECIMEN_TYPE_C] [decimal](38, 0) NULL,
	[COLL_PRTR_OVRIDE_YN] [varchar](1) NULL,
 CONSTRAINT [PK_SSIS_Specimen] PRIMARY KEY CLUSTERED 
	(
		[SPECIMEN_ID] ASC
	) 
) 
GO



IF OBJECT_ID(N'dbo.SSIS_CommentSynopticSpecimenLevel', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CommentSynopticSpecimenLevel
END 

CREATE TABLE [dbo].[SSIS_CommentSynopticSpecimenLevel](
	[SYNOPTIC_ID] [decimal](38, 0) NULL,
	[SYNOPIC_LINE] INT NULL,
	[SPECIMEN_ID] [decimal](38, 0) NULL,
	[K_SPECIMEN_KEY] [decimal](38, 0) NULL,
	[SPECIMEN_NUM] [varchar](1000) NULL,
	[K_REQUISITION_KEY] [decimal](38, 0) NULL,
	[CASE_NUM] [varchar](1000) NULL,
	[SPECIMEN_LIST] [varchar](1000) NULL,
	[RECORD_CREATION_DT] [datetime] NULL,
	[IS_SPECIMEN_LEVEL] INT NULL
) 
GO



IF OBJECT_ID(N'dbo.SSIS_CommentSynopticCaseLevel', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CommentSynopticCaseLevel
END 

CREATE TABLE [dbo].[SSIS_CommentSynopticCaseLevel](
	[SYNOPTIC_ID] [decimal](38, 0) NULL,
	[SYNOPIC_LINE] INT NULL,
	[SPECIMEN_ID] [decimal](38, 0) NULL,
	[K_SPECIMEN_KEY] [decimal](38, 0) NULL,
	[SPECIMEN_NUM] [varchar](1000) NULL,
	[K_REQUISITION_KEY] [decimal](38, 0) NULL,
	[CASE_NUM] [varchar](1000) NULL,
	[SPECIMEN_LIST] [varchar](1000) NULL,
	[RECORD_CREATION_DT] [datetime] NULL,
	[IS_SPECIMEN_LEVEL] INT NULL
) 
GO



IF OBJECT_ID(N'dbo.SSIS_CommentSynopticText', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CommentSynopticText
END 

CREATE TABLE [dbo].[SSIS_CommentSynopticText](
	[SYNOPTIC_ID] [decimal](38, 0) NULL,
	[SYNOPTIC_NAME] [varchar](1000) NULL,
	[SPECIMEN_LIST] [varchar](1000) NULL,
	[RECORD_CREATION_DT] [datetime] NULL,
	[INSTANT_OF_UPDATE_DTTM] [datetime] NULL,
	[MISSING_REQ_DATA_YN] [char](1) NULL,
	[HLV_ID] [decimal](38, 0) NULL,
	[ELEMENT_ID] [varchar](1000) NULL,
	[CUR_VALUE_DATETIME] [datetime] NULL,
	[CONTEXT_NAME] [varchar](1000) NULL,
	[CUR_VALUE_SOURCE] [varchar](1000) NULL,
	[RECORD_ID_NUMERIC] [decimal](38, 0) NULL,
	[REC_ARCHIVED_YN] [char](1) NULL,
	[CUR_VAL_UTC_DTTM] [datetime] NULL,
	[CLA_CON_NAME] [varchar](1000) NULL,
	[ABBREVIATION] [varchar](1000) NULL,
	[DATA_TYPE_C] [decimal](38, 0) NULL,
	[CONCEPT_ID] [varchar](1000) NULL,
	[PARENT_CONCEPT] [varchar](1000) NULL,
	[CONCEPT_HIERARCHY] [varchar](max) NULL,
	[RANK_SYNOPTIC] INT NULL
) 
GO



IF OBJECT_ID(N'dbo.SSIS_CommentPlainText', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CommentPlainText
END 

CREATE TABLE [dbo].[SSIS_CommentPlainText](
	[RESULT_ID] [decimal](38, 0) NULL,
	[GROUP_LINE] INT NULL,
	[VALUE_LINE] INT NULL,
	[COMP_NAME] [varchar](1000) NULL,	 	 
	[COMMENT_TYPE] [varchar](100) NULL,	 
	[COMPONENT_ID] [decimal](38, 0) NULL,	  
	[COMPONENT_INST] [datetime] NULL,
	[SPECIMENS_ID][decimal](38, 0) NULL,
	[REQUISITION_ID] [decimal](38, 0) NULL,
	[MULT_LN_VAL_STORAGE] [varchar](max) NULL
) 
GO


IF OBJECT_ID(N'dbo.SSIS_CommentRTFText', N'U') IS NOT NULL
BEGIN
	Drop Table dbo.SSIS_CommentRTFText
END 

CREATE TABLE [dbo].[SSIS_CommentRTFText](
	[ORDER_ID] [decimal](38, 0) NULL,
	[RESULT_ID] [decimal](38, 0) NULL,
	[CONTACT_DATE_REAL] [decimal](38, 5) NULL,
	[LINE_RTF_CMT] INT NULL,
	[CONTACT_DATE] [datetime] NULL, 
	[RTF_VAL_CMT] [varchar](MAX) NULL,
	[RES_ORDER_ID] [decimal](38, 0) NULL,
	[RES_SPECIMEN_ID] [decimal](38, 0) NULL,
	[RES_SPECIMEN] [varchar](1000) NULL,
	[SPECIMENS_ID] [decimal](38, 0) NULL,
	[COMP_RES_UTC_DTTM] [datetime] NULL, 
	[COMPONENT_ID] [decimal](38, 0) NULL,
	[COMP_NAME] [varchar](1000) NULL,
	[COMMENT_TYPE] [varchar](100) NULL,
	[REQUISITION_ID] [decimal](38, 0) NULL,	 	 
	[LINE_RES_SPE] INT NULL,
	[RANK_RES_DB_MAIN] INT NULL,
	[RANK_RES_SPECIMENS]INT NULL
) 
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenSource' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenSource
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenDrawType' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenDrawType
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenStatus
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseType' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseType
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseTypeCategory' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseTypeCategory
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_PatientRace' AND IsActive = 1)
		Truncate Table dbo.SSIS_PatientRace
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseStatus
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_MatrialStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_MatrialStatus
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Language' AND IsActive = 1)
		Truncate Table dbo.SSIS_Language
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Gender' AND IsActive = 1)
		Truncate Table dbo.SSIS_Gender
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseFlag' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseFlag
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_EthnicGroup' AND IsActive = 1)
		Truncate Table dbo.SSIS_EthnicGroup
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenType' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenType 
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Lab' AND IsActive = 1)
		Truncate Table dbo.SSIS_Lab
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Specimen' AND IsActive = 1)
		Truncate Table dbo.SSIS_Specimen
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseData' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseData
	--IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticSpecimenLevel' AND IsActive = 1)
	--	Truncate Table dbo.SSIS_CommentSynopticSpecimenLevel
	--IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticCaseLevel' AND IsActive = 1)
	--	Truncate Table dbo.SSIS_CommentSynopticCaseLevel
	--IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticText' AND IsActive = 1)
	--	Truncate Table dbo.SSIS_CommentSynopticText
	--IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentPlainText' AND IsActive = 1)
	--	Truncate Table [dbo].[SSIS_CommentPlainText]
	--IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentRTFText' AND IsActive = 1)
	--	Truncate Table [dbo].[SSIS_CommentRTFText]
END
GO




CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_SpecimenSource] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenSource' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenSource	 
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_SpecimenDrawType] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenDrawType' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenDrawType 
END
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_SpecimenStatus] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenStatus
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CaseType] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseType' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseType
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CaseTypeCategory] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseTypeCategory' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseTypeCategory
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_PatientRace] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_PatientRace' AND IsActive = 1)
		Truncate Table dbo.SSIS_PatientRace
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CaseStatus] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseStatus
END
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_MatrialStatus] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_MatrialStatus' AND IsActive = 1)
		Truncate Table dbo.SSIS_MatrialStatus
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_Language] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Language' AND IsActive = 1)
		Truncate Table dbo.SSIS_Language
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_Gender] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Gender' AND IsActive = 1)
		Truncate Table dbo.SSIS_Gender
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CaseFlag] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseFlag' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseFlag
END
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_EthnicGroup] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_EthnicGroup' AND IsActive = 1)
		Truncate Table dbo.SSIS_EthnicGroup
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_SpecimenType] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_SpecimenType' AND IsActive = 1)
		Truncate Table dbo.SSIS_SpecimenType 
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_Lab] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Lab' AND IsActive = 1)
		Truncate Table dbo.SSIS_Lab
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_Specimen] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_Specimen' AND IsActive = 1)
		Truncate Table dbo.SSIS_Specimen
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CaseData] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CaseData' AND IsActive = 1)
		Truncate Table dbo.SSIS_CaseData
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CommentSynopticLevel] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticSpecimenLevel' AND IsActive = 1)
		Truncate Table dbo.SSIS_CommentSynopticSpecimenLevel

	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticCaseLevel' AND IsActive = 1)
		Truncate Table dbo.SSIS_CommentSynopticCaseLevel

END
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CommentSynopticText] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentSynopticText' AND IsActive = 1)
		Truncate Table dbo.SSIS_CommentSynopticText

END
GO


CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CommentPlainText] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentPlainText' AND IsActive = 1)
		Truncate Table [dbo].[SSIS_CommentPlainText]

	DROP INDEX IF EXISTS IDX_SSIS_CommentPlainText_ResultId on SSIS_CommentPlainText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentPlainText_RequisitionId on SSIS_CommentPlainText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentPlainText_SpecimensId on SSIS_CommentPlainText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentPlainText_CompName on SSIS_CommentPlainText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentPlainText_CommentType on SSIS_CommentPlainText;
 
	 
END
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_TruncateTable_CommentRTFText] 
AS
BEGIN
	IF Exists (Select 0 from dbo.[SSIS_ConfigRun] Where [Name] = 'Truncate.OnLoad' AND [VAL] ='SSIS_CommentRTFText' AND IsActive = 1)
		Truncate Table [dbo].[SSIS_CommentRTFText]

	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_OrderId on SSIS_CommentRTFText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_ResultId on SSIS_CommentRTFText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_ContactDate on SSIS_CommentRTFText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_SpecimensId on SSIS_CommentRTFText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_RequisitionId on SSIS_CommentRTFText;
	DROP INDEX IF EXISTS IDX_SSIS_CommentRTFText_CompName on SSIS_CommentRTFText;
	 
END
GO
