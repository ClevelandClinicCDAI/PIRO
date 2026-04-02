SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE OR ALTER PROCEDURE [dbo].[P_SSIS_Seed_DataField]
AS
BEGIN
	SET NOCOUNT ON;

	-- Seed rows sourced from DataField.csv in the repo root.
	DECLARE @Seed TABLE(
		[DataFieldCategoryId] [int] NOT NULL,
		[DisplayName] [varchar](50) NOT NULL,
		[SolrField] [varchar](50) NOT NULL,
		[Code] [varchar](50) NOT NULL,
		[Sequence] [int] NOT NULL,
		[IsActive] [bit] NOT NULL
	);

	INSERT INTO @Seed (
		[DataFieldCategoryId],
		[DisplayName],
		[SolrField],
		[Code],
		[Sequence],
		[IsActive]
	)
	VALUES
		(4, 'Addendum', 'addend', 'ADDEND', 3, 1),
		(4, 'Comments', 'comment', 'COMMENT', 2, 1),
		(4, 'Final', 'final', 'FINAL', 1, 1),
		(4, 'Gross', 'gross', 'GROSS', 6, 1),
		(4, 'IntraOp', 'intraop', 'INTRAOP', 7, 1),
		(4, 'Resident', 'resident', 'RESIDENT', 8, 1),
		(4, 'Synoptic', 'synoptic', 'SYNOPTIC', 4, 1),
		(4, 'Clinical', 'clinical', 'CLINICAL', 5, 1),
		(4, 'Microscopic', 'microscopic', 'MICROSCOPIC', 9, 1),
		(3, 'Hospital', 'hospital', 'HOSPITAL', 1, 1),
		(3, 'Region', 'region', 'REGION', 1, 1),
		(2, 'Name', 'patientname', 'PATIENTNAME', 1, 1),
		(2, 'DOB', 'dob', 'PATIENTDOB', 1, 1),
		(2, 'Epi', 'epi', 'PATIENTEPI', 1, 1),
		(2, 'Mrn', 'mrn', 'PATIENTMRN', 1, 1),
		(2, 'Language', 'language', 'PATIENTLANGUAGE', 1, 1),
		(2, 'Ethnicity', 'ethnicity', 'PATIENTETHNICITY', 1, 1),
		(2, 'Sex', 'gender', 'PATIENTGENDER', 1, 1),
		(2, 'Death Date', 'deathdate', 'PATIENTDEATHDATE', 1, 1),
		(2, 'Deceased', 'isdeceased', 'PATIENTISDECEASED', 1, 1),
		(2, 'Race', 'race', 'PATIENTRACE', 1, 1),
		(2, 'Age', 'casepatientageyears', 'CASEPATIENTAGEYEARS', 1, 1),
		(1, 'Specimen Year', 'specimenyear', 'SPECIMENYEAR', 1, 1),
		(1, 'Case Number', 'casenumber', 'CASENUMBER', 1, 1),
		(1, 'Accession Date', 'accessiondate', 'ACCESSIONDATE', 1, 1),
		(1, 'Receive Date', 'receivedate', 'RECEIVEDATE', 1, 1),
		(1, 'Overdue Date', 'overduedate', 'OVERDUEDATE', 1, 1),
		(1, 'Collection Date', 'collectiondate', 'COLLECTIONDATE', 1, 1),
		(1, 'Signout Date', 'signoutdate', 'SIGNOUTDATE', 1, 1),
		(1, 'Case Status', 'casestatus', 'CASESTATUS', 1, 1),
		(1, 'Case Type', 'casetype', 'CASETYPE', 1, 1),
		(1, 'Review Type', 'reviewtype', 'REVIEWTYPE', 1, 1),
		(1, 'Case Category', 'casetypecategory', 'CASETYPECATEGORY', 1, 1),
		(1, 'Specialty', 'specialty', 'SPECIALTY', 1, 1),
		(1, 'Specialty Code', 'specialtycode', 'SPECIALTYCODE', 1, 1),
		(1, 'Specialty Category', 'specialtycategory', 'SPECIALTYCATEGORY', 1, 1),
		(1, 'Pathologist', 'interpreter', 'INTERPRETER', 1, 1),
		(1, 'Procedure Category', 'procedurecategory', 'PROCEDURECATEGORY', 1, 1),
		(1, 'Staff Name', 'staffname', 'STAFFNAME', 1, 0),
		(1, 'Specimen Number', 'specimennumber', 'SPECIMENNUMBER', 1, 1),
		(1, 'Results Contributors', 'pathologist', 'PATHOLOGIST', 1, 1);

	UPDATE DF
	SET
		[DisplayName] = S.[DisplayName],
		[SolrField] = S.[SolrField],
		[Sequence] = S.[Sequence],
		[IsActive] = S.[IsActive],
		[UpdateDate] = GETDATE(),
		[UpdateBy] = USER
	FROM [dbo].[DataField] DF
	JOIN @Seed S
	  ON DF.[DataFieldCategoryId] = S.[DataFieldCategoryId]
	 AND DF.[Code] = S.[Code];

	INSERT INTO [dbo].[DataField] (
		[DataFieldCategoryId],
		[DisplayName],
		[SolrField],
		[Code],
		[Sequence],
		[IsActive],
		[CreateDate],
		[CreateBy],
		[UpdateDate],
		[UpdateBy]
	)
	SELECT
		S.[DataFieldCategoryId],
		S.[DisplayName],
		S.[SolrField],
		S.[Code],
		S.[Sequence],
		S.[IsActive],
		GETDATE(),
		USER,
		NULL,
		NULL
	FROM @Seed S
	WHERE NOT EXISTS (
		SELECT 1
		FROM [dbo].[DataField] DF
		WHERE DF.[DataFieldCategoryId] = S.[DataFieldCategoryId]
		  AND DF.[Code] = S.[Code]
	);
END
GO
