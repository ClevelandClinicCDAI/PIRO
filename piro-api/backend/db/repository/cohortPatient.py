from core.constants import Constants
from sqlalchemy import text
from db.models.CohortPatient import CohortPatient
from db.models.CohortCase import CohortCase
from sqlalchemy.orm import Session
from viewmodel.cohortPatient import CohortPatientVMCreate, CohortPatientVM
from viewmodel.cohort import CohortDataVM
from typing import List


def create_new_cohortpatient(
    input: CohortPatientVMCreate, user: str, db: Session
):
    cohortpatient = CohortPatient(
        CohortId=input.cohortId,
        PatientMrn=input.mrn,
        IsActive=True,
        CreateBy=user,
    )
    db.add(cohortpatient)
    db.commit()
    db.refresh(cohortpatient)
    return cohortpatient


def create_new_cohortpatient_excel(
    cohortId: int, input: List[CohortDataVM], type: str, user: str, db: Session
):
    objects = []
    for rowData in input:
        if type == Constants.CohortTypeMrn:
            cohortpatient = CohortPatient(
                CohortId=cohortId,
                PatientMrn=rowData.data,
                PatientEpi="-",
                IsActive=True,
                CreateBy=user,
            )
            objects.append(cohortpatient)
        elif type == Constants.CohortTypeEpi:
            cohortpatient = CohortPatient(
                CohortId=cohortId,
                PatientMrn="-",
                PatientEpi=rowData.data,
                IsActive=True,
                CreateBy=user,
            )
            objects.append(cohortpatient)
        # db.add(cohortpatient)
    db.bulk_save_objects(objects)
    db.commit()
    return True


def create_new_cohortcase_excel(
    cohortId: int, input: List[CohortDataVM], user: str, db: Session
):
    objects = []
    for rowData in input:
        cohortpatient = CohortCase(
            CohortPatientId=None,
            CohortId=cohortId,
            PatientId=None,
            CaseNumber=rowData.data,
            CaseId=None,
            IsActive=True,
            LoadType=Constants.CohortTypeCase,
            IsSolrUpdated=False,
            CreateBy=user,
        )
        objects.append(cohortpatient)
        # db.add(cohortpatient)
    db.bulk_save_objects(objects)
    db.commit()
    return True


def get_cohortpatients(cohortId: int, db: Session):
    cohorts: List[CohortPatientVM] = []
    data = (
        db.query(CohortPatient)
        .filter(CohortPatient.CohortId == cohortId)
        .filter(CohortPatient.IsActive == True)  # noqa
        .all()
    )  # noqa
    for patient in data:
        item: CohortPatientVM = CohortPatientVM()
        item.cohortId = patient.CohortId
        item.mrn = patient.PatientMrn
        item.epi = patient.PatientEpi
        item.isfound = False if patient.PatientId == -1 else True
        cohorts.append(item)
    return cohorts


def delete_cohortpatient(cohortId: int, db: Session):
    sql = text(
        "Update dbo.CohortPatient set IsActive = 0, UpdateBy=user, UpdateDate=GETDATE() "
        + f"WHERE CohortId = {cohortId}"
    )
    db.execute(sql)
    db.commit()
    return True


def process_cohortpatient(cohortId: int, db: Session):
    sql = text(f"EXEC [dbo].[P_CohortPatient_Process] {cohortId}")
    db.execute(sql)
    db.commit()
    return True


def process_cohortpatient_case(cohortId: int, db: Session):
    sql = text(f"EXEC [dbo].[P_CohortPatient_Case_Process] {cohortId}")
    db.execute(sql)
    db.commit()
    return True
