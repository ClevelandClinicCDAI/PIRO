use PIRO_DEV
GO

DECLARE @CounterYear INT = 2022
DECLARE @CounterYearTo INT = 1960 -- 1990
DECLARE @WeekFrom INT = 0 
Declare @FromDate DATETIME, @ToDate DATETIME
DECLARE @LoopYear BIT = 1
WHILE ( @CounterYear >= @CounterYearTo)
BEGIN
	SET @WeekFrom = 0
	SET @LoopYear = 1
	WHILE (@LoopYear = 1)
	BEGIN
		SET @FromDate = DATEADD(Week, @WeekFrom, '01/01/' + CAST(@CounterYear as varchar))
		SET @ToDate = DATEADD(DAY, 7, @FromDate)
		SET @WeekFrom  = @WeekFrom  + 1
		IF @ToDate >= '12/31/' + CAST(@CounterYear as varchar)
		BEGIN
			SET @ToDate = '01/01/' + CAST((@CounterYear + 1) as varchar)
			SET @LoopYear = 0
		END
		PRINT CAST(@FromDate as varchar) + ' - ' + CAST(@ToDate as varchar)

		IF NOT EXISTS (SELECT 0 from [dbo].[STG_COPATH_LOG] WHERE [FromDate] = @FromDate OR [ToDate] = @ToDate)
		BEGIN
			INSERT INTO [dbo].[STG_COPATH_LOG]
					   ([FromDate]
					   ,[ToDate]
					   ,[RecordCount]
					   ,[SuccessCount]
					   ,[FailureCount]
					   ,[IsSuccess]
					   ,[IsProcessed]
					   ,[CreateDate]
					   ,[CreateBy]
					   ,[UpdateDate]
					   ,[UpdateBy])
			 VALUES
				   (@FromDate
				   ,@ToDate
				   ,0
				   ,0
				   ,0
				   ,0
				   ,0
				   ,GETDATE()
				   ,USER
				   ,NULL
				   ,NULL)
		END
	END
	SET @CounterYear  = @CounterYear  - 1
END


--select * from [STG_COPATH_LOG]
--truncate table [STG_COPATH_LOG]
--DBCC CHECKIDENT ('[STG_COPATH_LOG]', RESEED, 1);
 