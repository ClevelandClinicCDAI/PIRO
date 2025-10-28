from db.models.AnnotationConfiguration import AnnotationConfiguration
from sqlalchemy import asc
from sqlalchemy.orm import Session


def list_config(db: Session):
    configs = (
        db.query(AnnotationConfiguration)
        .order_by(asc(AnnotationConfiguration.RowIndex))
        .all()
    )
    return configs
