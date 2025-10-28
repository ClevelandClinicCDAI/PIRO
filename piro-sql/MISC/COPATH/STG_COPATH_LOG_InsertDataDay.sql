use PIRO_DEV
GO

DECLARE 
    @FromDate DATETIME, 
    @ToDate   DATETIME,
	@FromDateNew DATETIME, 
    @ToDateNew   DATETIME,
	@Days INT,
	@DayIndex INT,
	@IsProcess BIT; 

DECLARE cursor_record CURSOR
	FOR select FromDate, ToDate from STG_COPATH_LOG 
	Where IsProcessed = 1 and (FailureCount > 0 OR IsSuccess = 0);

OPEN cursor_record;

FETCH NEXT FROM cursor_record INTO 
    @FromDate, 
    @ToDate;

WHILE @@FETCH_STATUS = 0
BEGIN
	SET  @DAYS = DATEDIFF(DAY, @FromDate, @ToDate);
	--PRINT @DAYS
	IF @DAYS = 7
	BEGIN
		SET @IsProcess = 1;
		SET @DayIndex = 0;
		WHILE (@IsProcess = 1)
		BEGIN
			SET @FromDateNew = DATEADD(DAY, @DayIndex, @FromDate);
			SET @ToDateNew = DATEADD(DAY, 1, @FromDateNew);
			IF @ToDateNew <= @ToDate
			BEGIN
				PRINT CAST(@FromDateNew as varchar) + ' - ' + CAST(@ToDateNew as varchar)
				IF NOT EXISTS (SELECT 0 from [dbo].[STG_COPATH_LOG] WHERE [FromDate] = @FromDateNew AND [ToDate] = @ToDateNew)
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
						   (@FromDateNew
						   ,@ToDateNew
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
			ELSE
			BEGIN
				SET @IsProcess = 0;
			END
			SET @DayIndex = @DayIndex + 1
		END
	END
	FETCH NEXT FROM cursor_record INTO 
			@FromDate, 
			@ToDate; 
END

CLOSE cursor_record;

DEALLOCATE cursor_record;

--2007-01-01 00:00:00.000	2007-01-08 00:00:00.000
--select * from [STG_COPATH_LOG] order by Id desc
--truncate table [STG_COPATH_LOG]
--DBCC CHECKIDENT ('[STG_COPATH_LOG]', RESEED, 1);
 