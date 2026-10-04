"""Synchronize cases with ready whole-slide images from PostgreSQL to PIRO."""

import json

from sqlalchemy import text
from sqlalchemy.orm import Session

from tasks.loaders.concentriq_catalog import iter_catalog_batches
from tasks.utils.concentriq_setup import (
    get_concentriq_db_engine,
    get_concentriq_case_page_size,
)
from tasks.utils.logging_setup import get_logger

logger = get_logger()


class ConcentriqCaseLoader:
    def __init__(self, piro_engine=None):
        if piro_engine is None:
            from tasks.utils.database_setup import get_piro_db_engine
            piro_engine = get_piro_db_engine()
        self._piro_db_engine = piro_engine
        self._piro_db_session = Session(bind=piro_engine)

    def should_we_process_concentriq_data(self):
        value = self._piro_db_session.execute(text("""
            SELECT [Value] FROM dbo.ConcentriqConfig
            WHERE [Key] = 'CaseDetails.Get.Enabled' AND IsActive = 1
        """)).scalar()
        return str(value).strip().lower() in ("1", "true", "yes", "enabled")

    def close_db_connection(self):
        self._piro_db_session.close()
        self._piro_db_engine.dispose()

    def associate_concentriq_records_with_cases(self):
        try:
            self._piro_db_session.execute(text(
                "EXEC dbo.P_AIRFLOW_Concentriq_Case_Load"
            ))
            self._piro_db_session.commit()
        except Exception:
            self._piro_db_session.rollback()
            raise
        return True

    def delete_concentriq_case_data(self):
        try:
            self._piro_db_session.execute(text(
                "EXEC dbo.P_AIRFLOW_Concentriq_Case_Delete"
            ))
            self._piro_db_session.commit()
        except Exception:
            self._piro_db_session.rollback()
            raise
        return True

    def get_concentriq_data(self):
        """Stage a full snapshot; publish only after every batch succeeds."""
        engine = get_concentriq_db_engine()
        count = 0
        try:
            batch_size = get_concentriq_case_page_size()
            self._piro_db_session.execute(text("""
                CREATE TABLE #ConcentriqCatalog (
                    ConcentriqCaseId int NOT NULL,
                    CaseNumber varchar(100) COLLATE DATABASE_DEFAULT NOT NULL PRIMARY KEY,
                    AccessionDate datetime NULL
                )
            """))
            for items in iter_catalog_batches(engine, batch_size):
                self._piro_db_session.execute(text(
                    "EXEC dbo.P_AIRFLOW_Concentriq_Case_Sync @json_string=:items"
                ), {"items": json.dumps(items)})
                count += len(items)
                logger.info("Concentriq catalog records staged: %s", count)
            if count == 0:
                raise ValueError("Empty Concentriq image catalog; existing PIRO data retained")
            self._piro_db_session.execute(text(
                "EXEC dbo.P_AIRFLOW_Concentriq_Case_Sync @finalize=1"
            ))
            self._piro_db_session.execute(text("DROP TABLE #ConcentriqCatalog"))
            self._piro_db_session.commit()
            logger.info("Concentriq catalog synchronized: %s records", count)
        except Exception:
            self._piro_db_session.rollback()
            raise
        finally:
            engine.dispose()
        return True
