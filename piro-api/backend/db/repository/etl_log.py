import datetime

from db.models.ETL_Log import ETL_Log
from sqlalchemy import desc
from sqlalchemy.orm import Session


def list_log_month(days: int, db: Session):
    current_time = datetime.datetime.utcnow()
    thirty_days_ago = current_time - datetime.timedelta(days=days)

    logs = (
        db.query(ETL_Log)
        .filter(ETL_Log.CreatedDate > thirty_days_ago)
        .order_by(desc(ETL_Log.Id))
        .all()
    )
    return logs


def list_log(db: Session):
    logs = db.query(ETL_Log).order_by(desc(ETL_Log.Id)).all()
    return logs
