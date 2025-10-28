import decimal
from typing import List

from db.dict2Class import dict2Class
from db.models.AuditTrailCase import AuditTrailCase
from db.models.AuditTrailSearch import AuditTrailSearch
from exception.data_exception import DataException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

# from core.search_util import filter_str_object


def create_audit_search(
    userId: int,
    user: str,
    searchQuery: str,
    searchDisplay: str,
    searchUrl: str,
    advQuery: str,
    mrn: str,
    caseIds: List[int],
    total: int,
    exeuteTime: decimal,
    db: Session,
):
    search = AuditTrailSearch(
        UserId=userId,
        SearchQuery=searchQuery,
        SearchDisplay=searchDisplay,
        SearchUrl=searchUrl,
        AdvancedQuery="" if advQuery is None else advQuery,
        MRN="" if mrn is None else mrn,
        TotalHits=total,
        ExecutionTime=exeuteTime,
        CreateBy=user,
    )
    db.add(search)

    for caseId in caseIds:
        case = AuditTrailCase(
            AuditTrailSearch=search,
            UserId=userId,
            CaseId=caseId,
            CreateBy=user,
        )
        db.add(case)

    db.commit()
    return search


def list_audit_search(userId: int, db: Session):
    auditTrailSearch = (
        db.query(AuditTrailSearch)
        .filter(AuditTrailSearch.UserId == userId)
        .order_by(desc(AuditTrailSearch.AuditTrailSearchId))
        .limit(1000)
        .all()
    )
    return auditTrailSearch


def list_audit_search_unique(userId: int, db: Session):
    sql = text(
        "SELECT TOP 15 * FROM ( "
        + "SELECT AuditTrailSearchId, "
        + "SearchQuery, "
        + "SearchDisplay, "
        + "SearchUrl, "
        + "AdvancedQuery, "
        + "MRN, "
        + "TotalHits, "
        + "CreateDate, "
        + "ROW_NUMBER() OVER(PARTITION BY SearchQuery "
        + "ORDER BY AuditTrailSearchId DESC) AS RowNum "
        + f"FROM (Select Top 1000 * FROM AuditTrailSearch Where UserId ="
        f" {userId} ORDER BY  AuditTrailSearchId desc) DAT "
        + ") REC WHERE REC.RowNum = 1 Order by AuditTrailSearchId desc"
    )

    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class(
            {
                "AuditTrailSearchId": row[0],
                "SearchQuery": row[1],
                "SearchDisplay": row[2],
                "SearchUrl": row[3],
                "AdvancedQuery": row[4],
                "MRN": row[5],
                "TotalHits": row[6],
                "CreateDate": row[7],
            }
        )
        result.append(item)
    return result


def get_audit_search(auditTrailSearchId: int, db: Session):
    auditTrailSearch = (
        db.query(AuditTrailSearch)
        .filter(AuditTrailSearch.AuditTrailSearchId == auditTrailSearchId)
        .first()
    )
    if auditTrailSearch is None:
        raise DataException("AuditTrailSearch does not exist")
    return auditTrailSearch
