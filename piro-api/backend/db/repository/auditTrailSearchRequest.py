from db.models.AuditTrailSearchRequest import AuditTrailSearchRequest

from sqlalchemy.orm import Session


def create_audit_search_request(
    userId: int, user: str, searchRequestId: int, action: str, db: Session
):
    audit = AuditTrailSearchRequest(
        UserId=userId,
        SearchRequestId=searchRequestId,
        Action=action,
        CreateBy=user,
    )
    db.add(audit)
    db.commit()
