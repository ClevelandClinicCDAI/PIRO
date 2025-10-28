USE [msdb]
GO

/****** Object:  Job [PIRO_Clarity_Delta_Load]    Script Date: 9/9/2025 4:54:19 PM ******/
BEGIN TRANSACTION
DECLARE @ReturnCode INT
SELECT @ReturnCode = 0
/****** Object:  JobCategory [[Uncategorized (Local)]]    Script Date: 9/9/2025 4:54:20 PM ******/
IF NOT EXISTS (SELECT name FROM msdb.dbo.syscategories WHERE name=N'[Uncategorized (Local)]' AND category_class=1)
BEGIN
EXEC @ReturnCode = msdb.dbo.sp_add_category @class=N'JOB', @type=N'LOCAL', @name=N'[Uncategorized (Local)]'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback

END

DECLARE @jobId BINARY(16)
EXEC @ReturnCode =  msdb.dbo.sp_add_job @job_name=N'PIRO_Clarity_Delta_Load',
		@enabled=1,
		@notify_level_eventlog=2,
		@notify_level_email=2,
		@notify_level_netsend=0,
		@notify_level_page=0,
		@delete_level=0,
		@description=N'PIRO_Clarity_Delta_Load loads data from CLARITY into the PIRO Staging tables.',
		@category_name=N'[Uncategorized (Local)]',
		@owner_login_name=N'[username]',
		@notify_email_operator_name=N'PIRO_Team', @job_id = @jobId OUTPUT
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [_run_main_delta_daily.dtsx]    Script Date: 9/9/2025 4:54:20 PM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'_run_main_delta_daily.dtsx',
		@step_id=1,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\PIRO_PROD\piro-ssis\_run_main_delta_daily.dtsx\"" /SERVER "\"[host]\[instance]\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'[service_account]'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [_send_success_email]    Script Date: 9/9/2025 4:54:20 PM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'_send_success_email',
		@step_id=2,
		@cmdexec_success_code=0,
		@on_success_action=1,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'CmdExec',
		@command=N'sqlcmd -S [host]\[instance] -d msdb -E -Q "EXEC msdb.dbo.sp_send_dbmail @profile_name=''DBAMailProfile'', @from_address = ''PIRO SSIS PROD  <[from_address]>'', @recipients=''[recipients]'', @subject=''PIRO PROD - SSIS Clarity Delta Load job'', @body=''PIRO PROD - SSIS Clarity Delta Load job ran successfully.''"
',
		@flags=0,
		@proxy_name=N'[service_account]'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_update_job @job_id = @jobId, @start_step_id = 1
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_add_jobschedule @job_id=@jobId, @name=N'Run_daily_16:00',
		@enabled=1,
		@freq_type=4,
		@freq_interval=1,
		@freq_subday_type=1,
		@freq_subday_interval=0,
		@freq_relative_interval=0,
		@freq_recurrence_factor=0,
		@active_start_date=20250909,
		@active_end_date=99991231,
		@active_start_time=160000,
		@active_end_time=235959,
		@schedule_uid=N'[schedule_uid]'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_add_jobserver @job_id = @jobId, @server_name = N'(local)'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
COMMIT TRANSACTION
GOTO EndSave
QuitWithRollback:
    IF (@@TRANCOUNT > 0) ROLLBACK TRANSACTION
EndSave:
GO


