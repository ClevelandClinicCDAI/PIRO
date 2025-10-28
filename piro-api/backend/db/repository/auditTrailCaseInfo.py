from db.models.AuditTrailCaseInfo import AuditTrailCaseInfo

from sqlalchemy.orm import Session


def create_audit_case(userId: int, user: str, caseId: int, db: Session):
    audit = AuditTrailCaseInfo(
        UserId=userId,
        CaseId=caseId,
        CreateBy=user,
    )
    db.add(audit)
    db.commit()
