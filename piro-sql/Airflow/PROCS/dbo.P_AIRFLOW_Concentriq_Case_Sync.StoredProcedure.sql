CREATE OR ALTER PROCEDURE dbo.P_AIRFLOW_Concentriq_Case_Sync
    @json_string nvarchar(max) = NULL,
    @finalize bit = 0,
    @start bit = 0,
    @full_snapshot bit = 1,
    @last_case_id int = 0
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    IF @@TRANCOUNT = 0
        THROW 50001, 'Catalog synchronization requires a caller transaction.', 1;
    IF OBJECT_ID('tempdb..#ConcentriqCatalog') IS NULL
        THROW 50002, 'Catalog staging table is missing.', 1;

    IF @start = 1 OR @finalize = 1
    BEGIN
        DECLARE @lock_result int;
        EXEC @lock_result = sys.sp_getapplock
            @Resource = 'PIRO.ConcentriqCatalog', @LockMode = 'Exclusive',
            @LockOwner = 'Transaction', @LockTimeout = 60000;
        IF @lock_result < 0
            THROW 50004, 'Could not acquire Concentriq synchronization lock.', 1;
    END;

    IF @start = 1
    BEGIN
        SELECT COALESCE((SELECT CONVERT(int, [Value])
                        FROM dbo.ConcentriqConfig
                        WHERE [Key] = 'CaseDetails.Get.LastCaseId' AND IsActive = 1), 0);
        RETURN;
    END;

    IF @finalize = 0
    BEGIN
        -- Duplicate accessions (including across batches) fail the entire refresh.
        INSERT INTO #ConcentriqCatalog(ConcentriqCaseId, CaseNumber, AccessionDate)
        SELECT id, accessionId,
               CONVERT(datetime, CONVERT(datetimeoffset, accessionDate, 127))
        FROM OPENJSON(@json_string)
        WITH (id int, accessionId varchar(100), accessionDate varchar(100));
        RETURN;
    END;

    IF NOT EXISTS (SELECT 1 FROM #ConcentriqCatalog)
        THROW 50003, 'Empty image catalog; existing data retained.', 1;

    UPDATE cc
        SET ConcentriqCaseId = catalog.ConcentriqCaseId,
            AccessionDate = catalog.AccessionDate, IsActive = 1,
            UpdateDate = GETDATE(), UpdateBy = USER_NAME()
    FROM dbo.ConcentriqCase cc
    JOIN #ConcentriqCatalog catalog ON catalog.CaseNumber = cc.CaseNumber
    WHERE cc.IsActive = 0 OR cc.ConcentriqCaseId <> catalog.ConcentriqCaseId
       OR cc.AccessionDate <> catalog.AccessionDate
       OR (cc.AccessionDate IS NULL AND catalog.AccessionDate IS NOT NULL)
       OR (cc.AccessionDate IS NOT NULL AND catalog.AccessionDate IS NULL);

    INSERT INTO dbo.ConcentriqCase
        (ConcentriqCaseId, CaseId, CaseNumber, AccessionDate, IsActive, CreateDate, CreateBy)
    SELECT catalog.ConcentriqCaseId, -1, catalog.CaseNumber, catalog.AccessionDate,
           1, GETDATE(), USER_NAME()
    FROM #ConcentriqCatalog catalog
    WHERE NOT EXISTS (SELECT 1 FROM dbo.ConcentriqCase cc
                      WHERE cc.CaseNumber = catalog.CaseNumber);

    -- A limited slice cannot establish that other cases have lost their images.
    IF @full_snapshot = 1
    BEGIN
        UPDATE cc SET IsActive = 0, UpdateDate = GETDATE(), UpdateBy = USER_NAME()
        FROM dbo.ConcentriqCase cc
        WHERE cc.IsActive = 1 AND NOT EXISTS
            (SELECT 1 FROM #ConcentriqCatalog catalog WHERE catalog.CaseNumber = cc.CaseNumber);
    END;

    EXEC dbo.P_AIRFLOW_Concentriq_Case_Load;

    -- Commit the checkpoint with the catalog so failed runs retry the same slice.
    UPDATE dbo.ConcentriqConfig
        SET [Value] = CONVERT(varchar(1000), @last_case_id), IsActive = 1,
            UpdateDate = GETDATE(), UpdateBy = USER_NAME()
    WHERE [Key] = 'CaseDetails.Get.LastCaseId';
    IF @@ROWCOUNT = 0
        INSERT INTO dbo.ConcentriqConfig
            ([Key], [Value], IsActive, CreateDate, CreateBy)
        VALUES ('CaseDetails.Get.LastCaseId', CONVERT(varchar(1000), @last_case_id),
                1, GETDATE(), USER_NAME());
END
GO
