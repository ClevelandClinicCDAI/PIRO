from sqlalchemy import text
from db.models.CohortCase import CohortCase
from sqlalchemy.orm import Session
from viewmodel.cohortCase import CohortCaseVM
from typing import List


def delete_cohortcase(cohortId: int, db: Session):
    sql = text(
        "Update dbo.CohortCase set IsActive = 0, IsSolrUpdated = 0, UpdateBy=user, UpdateDate=GETDATE() "
        + f"WHERE CohortId = {cohortId}"
    )
    db.execute(sql)
    db.commit()
    return True


def process_cohortcase(cohortId: int, db: Session):
    sql = text(f"EXEC [dbo].[P_CohortCase_Process] {cohortId}")
    db.execute(sql)
    db.commit()
    return True


def get_cohortcases(cohortId: int, db: Session):
    cohorts: List[CohortCaseVM] = []
    data = (
        db.query(CohortCase)
        .filter(CohortCase.CohortId == cohortId)
        .filter(CohortCase.IsActive == True)  # noqa
        .all()
    )  # noqa
    for caseData in data:
        item: CohortCaseVM = CohortCaseVM()
        item.cohortId = caseData.CohortId
        item.case = caseData.CaseNumber
        item.isfound = False if caseData.CaseId == -1 else True
        cohorts.append(item)
    return cohorts
