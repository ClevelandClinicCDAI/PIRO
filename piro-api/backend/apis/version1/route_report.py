from core.auth_bearer import JWTBearer
from db.repository.report import report_audittrail
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.views.auditReport import AuditReportVM

router = APIRouter()


@router.get(
    "/audittrailsearch",
    dependencies=[Depends(JWTBearer())],
    response_model=AuditReportVM,
)
async def get_audittrail_search(db: Session = Depends(get_db)):
    audits = report_audittrail(db=db)
    labels = []
    searchData = []
    caseData = []
    for data in audits:
        labels.append(data.MonthLabel)
        searchData.append(data.SearchCount)
        caseData.append(data.CaseCount)
    return {"Labels": labels, "SearchData": searchData, "CaseData": caseData}
