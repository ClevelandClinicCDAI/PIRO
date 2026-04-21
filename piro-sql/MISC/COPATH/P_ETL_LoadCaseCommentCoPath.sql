Use PIRO

-- =============================================
-- Author:		Ven
-- Create date: 7/11/2023
-- Description:	Loads CaseComment Data from Staging to Transaction Table.
-- =============================================
IF (OBJECT_ID('dbo.P_ETL_LoadCaseCommentCoPath') IS NOT NULL)
	DROP PROCEDURE dbo.P_ETL_LoadCaseCommentCoPath;
GO

CREATE PROCEDURE dbo.P_ETL_LoadCaseCommentCoPath 
@Insert BIT = 0,
@Update BIT = 0
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;
	DECLARE @RowsInserted INT = 0 
	DECLARE @RowsUpdated INT = 0 
	DECLARE @RowsToBeInserted INT  = 0 
	DECLARE @RowsToBeUpdated INT = 0 
	DECLARE @Table Varchar(100) = 'CaseCommentCoPath'
	DECLARE @CommentTypeIdNull INT
	DECLARE @EndTime datetime
	DECLARE @StartTime datetime, @LoadTime INT
	SELECT @StartTime=GETDATE() 
	 

		BEGIN TRY
			IF ISNULL(@Insert, 0) = 0 AND ISNULL(@Update, 0) = 0
			BEGIN
				;THROW 50001, 'P_ETL_LoadCaseCommentCoPath requires @Insert = 1 and/or @Update = 1.', 1;
			END
			 
			IF @Insert = 1
			BEGIN
			DROP INDEX IF EXISTS idx_CaseCommentCoPath_CaseId
			ON CaseCommentCoPath;

			DROP INDEX IF EXISTS idx_CaseCommentCoPath_CaseNum
			ON CaseCommentCoPath;
		
			DROP INDEX IF EXISTS idx_CaseCommentCoPath_RefId
			ON CaseCommentCoPath;

			TRUNCATE TABLE dbo.CaseCommentCoPath

			SELECT @RowsToBeInserted = COUNT(0) From dbo.ETLCopathCaseComment   
			INSERT INTO [dbo].[CaseCommentCoPath]
			   ([CaseId]
			   ,[CommentTypeId]
			   ,[Text]
			   ,[RtfText]
			   ,[StatusDate]
			   ,[SpecYear]
			   ,[RefId]
			   ,[RefSpecimenId]
			   ,[RefCaseNum]
			   ,[RefSpecimenNum]
			   ,[RefTextType]
			   ,[CreateDate]
			   ,[CreateBy]
			   ,[UpdateDate]
			   ,[UpdateBy]
			   ,IsTextUpdated)
			SELECT  
				C.CaseId
					,CASE texttype_id
						WHEN '$n-final' THEN 3
						WHEN '$final' THEN 3
						WHEN '$n-gross' THEN 3
						WHEN '$frodx1' THEN 5
						WHEN '$gross' THEN 4
						WHEN '$othgross' THEN 4
						WHEN '$n-othergross' THEN 4
						WHEN '$clindx' THEN 10
						WHEN '$micro' THEN 12
						WHEN '$synop' THEN 7
						ELSE 8
					END
				--,[text_data_text]
				--,[text_data_rtf]
				,NULL
				,NULL
				,[status_date]
				,[specnum_year]
				,[Id]
				,[specimen_id]
				,[CaseNum]
				,[specnum_formatted]
				,[texttype_id]
				,getdate()
				,User
				,NULL
				,NULL
				,0
			FROM [dbo].[ETLCopathCaseComment] EC
			JOIN [dbo].[Case] C on EC.CaseNum = C.CaseNumber
		 
 
			SET @RowsInserted = @@ROWCOUNT

			CREATE INDEX idx_CaseCommentCoPath_RefId
			ON CaseCommentCoPath (RefId);

			CREATE INDEX idx_CaseCommentCoPath_CaseId
			ON CaseCommentCoPath (CaseId);
	 
			CREATE INDEX idx_CaseCommentCoPath_CaseNum
			ON CaseCommentCoPath (RefCaseNum);
		END


			IF @Update = 1 
			BEGIN
				DECLARE @MaxId INT, @FromId INT = 0, @ToId INT = 0, @BulkSize INT = 100000;
				SELECT @RowsToBeUpdated = COUNT(0)
				FROM [dbo].CaseCommentCoPath C
				JOIN [dbo].[ETLCopathCaseComment] EC on C.RefId = EC.id
				WHERE C.IsTextUpdated = 0;
			
				SET @MaxId = (select MAx(Id) from [ETLCopathCaseComment] )

				IF ISNULL(@RowsToBeUpdated, 0) > 0 AND @MaxId IS NOT NULL
				BEGIN
					While (@ToId < @MaxId)
					BEGIN
						SET @ToId = @FromId + @BulkSize;
						PRINT CAST(@FromId as VARCHAR) + ' -- ' + CAST(@ToId as VARCHAR) 
						Update C
						SET 		
						[RtfText] = EC.text_data_rtf,
						[Text] = EC.text_data_text,
						IsTextUpdated = 1
						FROM [dbo].CaseCommentCoPath C
						JOIN [dbo].[ETLCopathCaseComment] EC on C.RefId = EC.id
						WHERE EC.Id >= @FromId AND EC.Id < @ToId AND IsTextUpdated = 0

						SET @RowsUpdated = @RowsUpdated + @@ROWCOUNT

						SET @FromId = @ToId

					END
				END
			END
		print 'Insert End'
		SELECT @EndTime=GETDATE()
		SET @LoadTime = DATEDIFF(SECOND, @StartTime, @EndTime)
		EXEC dbo.P_SSIS_LogMainTable @Table,
									@RowsToBeInserted,
									@RowsInserted,
									@RowsToBeUpdated,
									@RowsUpdated,
									1,
									'',
									@LoadTime
	
		END TRY 
		BEGIN CATCH 
			DECLARE @ERROR VARCHAR(MAX) = ERROR_MESSAGE()
			SELECT @EndTime=GETDATE()
			SET @LoadTime = DATEDIFF(SECOND, @StartTime, @EndTime)
			IF XACT_STATE() <> -1
			BEGIN
				EXEC dbo.P_SSIS_LogMainTable @Table,
									@RowsToBeInserted,
									@RowsInserted,
									@RowsToBeUpdated,
									@RowsUpdated,
									0,
									@ERROR,
									@LoadTime
			END
			;THROW;
		END CATCH
END
GO

 

 --select * from [CaseCommentCoPath]
--select count(0) from 
--[dbo].CaseCommentCoPath C
--JOIN [dbo].[ETLCopathCaseComment] EC on C.[RefCaseNum] = EC.CaseNum
--WHERE EC.Id > 250000*2 AND EC.Id < 250000*3

--select * from [ETLCopathCaseComment]
----43325105

 /*
 
 DECLARE @MaxId INT, @FromId INT = 0, @ToId INT = 0, @BulkSize INT = 200000;
 --DECLARE @MaxId INT, @FromId INT = 8593014, @ToId INT = 0, @BulkSize INT = 12;
 DECLARE @RowsUpdated INT
		
		SET @MaxId = (select MAx(Id) from [ETLCopathCaseComment] )
		--SET @MaxId = @FromId + @BulkSize
		While (@ToId < @MaxId)
		BEGIN
			SET @ToId = @FromId + @BulkSize;
			PRINT CAST(@FromId as VARCHAR) + ' -- ' + CAST(@ToId as VARCHAR) 
			 WAITFOR DELAY '00:00:01'
			Update C
			SET 		
			[RtfText] = EC.text_data_rtf,
			[Text] = EC.text_data_text,
			IsTextUpdated = 1
			FROM [dbo].CaseCommentCoPath C
			JOIN [dbo].[ETLCopathCaseComment] EC on C.RefId = EC.id
			WHERE EC.Id >= @FromId AND EC.Id < @ToId  

			SET @RowsUpdated = @RowsUpdated + @@ROWCOUNT

			SET @FromId = @ToId

		END
		PRINT @RowsUpdated

 select count(0) from CaseCommentCoPath -- 29386053
 select count(0) from [ETLCopathCaseComment] -- 43295805

  select top 10 * from CaseCommentCoPath -- 29386053
 select top 10 * from [ETLCopathCaseComment] -- 43295805
select * from ETLCopathCaseComment where specnum_formatted = 'S17-152130'
select * from CaseCommentCoPath where refcasenum = 'S17-152130'
select * from CaseCommentCoPath where refId = 8593022
 */


-- P_ETL_LoadCaseCommentCoPath 1, 0
-- P_ETL_LoadCaseCommentCoPath 0, 1
