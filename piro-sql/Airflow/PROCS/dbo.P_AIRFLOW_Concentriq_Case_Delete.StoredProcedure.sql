CREATE OR ALTER PROCEDURE dbo.P_AIRFLOW_Concentriq_Case_Delete
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    BEGIN TRANSACTION;
    BEGIN TRY
        DECLARE @lock_result int;
        EXEC @lock_result = sys.sp_getapplock
            @Resource = 'PIRO.ConcentriqCatalog', @LockMode = 'Exclusive',
            @LockOwner = 'Transaction', @LockTimeout = 60000;
        IF @lock_result < 0
            THROW 50004, 'Could not acquire Concentriq synchronization lock.', 1;
        TRUNCATE TABLE dbo.ConcentriqCase;
        UPDATE dbo.ConcentriqConfig
            SET [Value] = '0', UpdateDate = GETDATE(), UpdateBy = USER_NAME()
        WHERE [Key] = 'CaseDetails.Get.LastCaseId';
        EXEC dbo.P_AIRFLOW_Concentriq_Case_Load;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END
GO
