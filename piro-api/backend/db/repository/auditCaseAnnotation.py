from db.models.AuditCaseAnnotation import AuditCaseAnnotation
from sqlalchemy.orm import Session
from sqlalchemy import desc


def list_case_annotation(caseId: int, configId: int, db: Session):
    audit = (
        db.query(AuditCaseAnnotation)
        .filter(AuditCaseAnnotation.CaseId == caseId)
        .filter(AuditCaseAnnotation.AnnotationConfigurationId == configId)
        .order_by(desc(AuditCaseAnnotation.AuditCaseAnnotationId))
        .all()
    )
    return audit
