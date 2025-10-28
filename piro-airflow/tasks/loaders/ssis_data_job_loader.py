from sqlalchemy import text
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session
from tasks.utils.database_ssis_setup import get_piro_db_engine
from tasks.utils.database_ssis_setup import get_piro_db_session
from tasks.utils.logging_setup import get_logger

logger = get_logger()


class SsisDataJobLoader:
    """Class for loading case data into SOLR. The source data table is CohortCase_Delta. SOLR import handler is triggered for the data load"""  # noqa: E501

    def __init__(self):
        logger.info("SsisDataJobLoader constructor-Start")

        self._piro_db_engine: Engine = get_piro_db_engine()
        self._piro_db_connection: Connection = self._piro_db_engine.connect()
        self._piro_db_session: Session = get_piro_db_session(
            engine=self._piro_db_engine
        )
        logger.info("SsisDataJobLoader constructor-End")

    def _run_delta_load_job(self):
        logger.info("_run_delta_load_job -Start")
        sql = text("EXECUTE msdb.dbo.sp_start_job N'PIRO_Clarity_Delta_Load';")
        # sql = text("""EXECUTE msdb.dbo.sp_start_job N'PIRO_Test_Package';""")

        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        logger.info("_run_delta_load_job -End")
        return True

    def _run_full_load_job(self):
        logger.info("_run_full_load_job -Start")
        sql = text(
            "EXECUTE msdb.dbo.sp_start_job N'PIRO_Clarity_Full_Data_Load';"
        )

        self._piro_db_session.execute(sql)
        self._piro_db_session.commit()
        logger.info("_run_full_load_job -End")
        return True

    def _close_db_connection(self) -> None:
        """Close any connections to the database."""
        self._piro_db_session.close()
        self._piro_db_connection.close()
