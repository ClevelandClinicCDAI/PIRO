from db.models.Cohort import Cohort
from db.models.CohortPatient import CohortPatient
from exception.data_exception import DataException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from viewmodel.cohort import CohortDetailsVM
from db.dict2Class import dict2Class
from core.constants import Constants


def create_new_cohort(
    name: str,
    desc: str,
    disease: str,
    display: bool,
    dataType: str,
    userId: int,
    user: str,
    db: Session,
):
    cohort = Cohort(
        Name=name,
        Description=desc,
        Disease="" if disease is None else disease,
        IsFacetDisplay=display,
        UserId=userId,
        IsActive=True,
        LoadType=dataType,
        IsSolrUpdated=False,
        CreateBy=user,
    )

    db.add(cohort)
    db.commit()
    db.refresh(cohort)
    return cohort


def update_cohort(
    cohortId: int,
    name: str,
    desc: str,
    disease: str,
    display: bool,
    userId: int,
    user: str,
    db: Session,
):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.CohortId == cohortId)
        .filter(Cohort.IsActive == True)  # noqa
        .first()
    )
    if cohort is not None:
        cohort.Name = name
        cohort.Description = desc
        cohort.Disease = disease
        cohort.IsFacetDisplay = display
        cohort.UserId = userId
        cohort.IsActive = True
        cohort.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Cohort does not exist")
    return cohort


def list_cohort(userId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.UserId == userId)  # noqa
        .filter(Cohort.IsActive == True)  # noqa
        .filter(Cohort.IsFacetDisplay == True)  # noqa
        .order_by(desc(Cohort.CohortId))
        .all()
    )
    return cohort


def list_cohort_active(userId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.UserId == userId)
        .filter(Cohort.IsActive == True)  # noqa
        .order_by(desc(Cohort.CohortId))
        .all()
    )
    return cohort


def get_cohort_custom(cohortId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.CohortId == cohortId)
        .filter(Cohort.IsActive == True)
        .first()
    )  # noqa
    if cohort is None:
        raise DataException("Cohort does not exist")
    # cohortPatientTotal = db.query(CohortPatient).filter(Cohort.CohortId == cohortId).count()    # noqa
    # cohortPatientMatched = db.query(CohortPatient).filter(Cohort.CohortId == cohortId).filter(Cohort.PatientId != -1).count()   # noqa

    item = dict2Class(
        {
            "CohortId": cohort.CohortId,
            "Name": cohort.Name,
            "Description": cohort.Description,
            "Disease": cohort.Disease,
            "IsActive": cohort.IsActive,
            "Total": cohort.PatientTotal,
            "Matched": cohort.PatientMatched,
        }
    )
    return item


def get_cohort(cohortId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.CohortId == cohortId)
        .filter(Cohort.IsActive == True)
        .first()
    )  # noqa
    return cohort


def get_cohort_data(cohortId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.CohortId == cohortId)
        .filter(Cohort.IsActive == True)
        .first()
    )  # noqa
    if cohort is None:
        raise DataException("Cohort does not exist")
    if (
        cohort.LoadType == Constants.CohortTypeMrn
        or cohort.LoadType == Constants.CohortTypeEpi
    ):
        cohortPatientTotal = (
            db.query(CohortPatient)
            .filter(CohortPatient.CohortId == cohortId)
            .filter(CohortPatient.IsActive == True)
            .count()
        )  # noqa
        cohortPatientMatched = (
            db.query(CohortPatient)
            .filter(CohortPatient.CohortId == cohortId)
            .filter(CohortPatient.PatientId != -1)
            .filter(CohortPatient.IsActive == True)
            .count()
        )  # noqa

        cohortCaseTotal_query = text(
            f"""SELECT count(distinct CaseId) From [dbo].[CohortCase] Where CohortId = {cohortId} AND IsActive = 1"""
        )
        cohortCaseTotal = db.execute(cohortCaseTotal_query).scalar()
        cohortCaseMatched = 0
    else:
        cohortPatientTotal = 0
        cohortPatientMatched = 0
        cohortCaseTotal_query = text(
            f"""SELECT count(distinct CaseId) From [dbo].[CohortCase] Where CohortId = {cohortId} AND IsActive = 1"""
        )
        cohortCaseTotal = db.execute(cohortCaseTotal_query).scalar()

        cohortCaseMatched_query = text(
            f"""SELECT count(distinct CaseId) From [dbo].[CohortCase] Where CohortId = {cohortId} AND IsActive = 1 AND CaseId <> -1"""
        )
        cohortCaseMatched = db.execute(cohortCaseMatched_query).scalar()

    item = CohortDetailsVM()
    item.cohortId = cohort.CohortId
    item.name = cohort.Name
    item.desc = cohort.Description
    item.disease = cohort.Disease
    item.display = cohort.IsFacetDisplay
    item.dataType = cohort.LoadType
    item.patientCount = cohortPatientTotal
    item.matched = cohortPatientMatched
    item.unmatched = cohortPatientTotal - cohortPatientMatched
    item.caseCount = cohortCaseTotal
    item.caseCountMatched = cohortCaseMatched
    return item


def delete_cohort(cohortId: int, db: Session):
    cohort = (
        db.query(Cohort)
        .filter(Cohort.CohortId == cohortId)
        .filter(Cohort.IsActive == True)  # noqa
        .first()
    )  # noqa
    if cohort is not None:
        cohort.IsActive = False
        cohort.IsSolrUpdated = False
        db.commit()
    else:
        raise DataException("Cohort does not exist")
    return True


def get_user_cohorts(userId: int, db: Session):
    sql = text("EXEC [dbo].[P_Cohort_All]  " + f"{userId}")

    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class(
            {
                "CohortId": row[0],
                "Name": row[1],
                "Description": row[2],
                "Disease": row[3],
                "IsFacetDisplay": row[4],
                "IsActive": row[5],
                "CaseCount": row[6],
                "PatientCountTotal": row[7],
                "PatientCountMatched": row[8],
                "PatientCountUnMatched": row[9],
                "Type": row[10],
            }
        )
        result.append(item)
    return result
