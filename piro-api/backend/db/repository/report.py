from db.views.VAuditTrail_Report import VAuditTrail_Report
from sqlalchemy import asc
from sqlalchemy.orm import Session
from db.dict2Class import dict2Class


def report_audittrail(db: Session):
    audits = (
        db.query(VAuditTrail_Report)
        .order_by(asc(VAuditTrail_Report.Date))
        .all()
    )
    result = []
    for data in audits:
        item = dict2Class(
            {
                "Date": data.Date,
                "MonthName": data.MonthName,
                "MonthLabel": f"{str(data.Month).zfill(2)}-{str(data.Year).zfill(2)}",
                "SearchCount": data.SearchCount,
                "CaseCount": data.CaseCount,
            }
        )
        result.append(item)
    return result
