from db.views.VCase import VCase
from db.views.VCaseMrn import VCaseMrn
from db.views.VCaseInterpreter import VCaseInterpreter
from db.views.VCaseStaff import VCaseStaff
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from core.config import settings
from db.repository.caseCommentSynoptic import (
    synoptic_specimen,
    synoptic_specimen_group,
)


def get_case(caseId: int, db: Session):
    case = db.query(VCase).filter(VCase.CaseId == caseId).first()
    if (
        case is not None
        and case.IsConcentriq == True
        and case.CaseConcentriqId > 0
    ):
        case.CaseConcentriqUrl = (
            f"{settings.CONCENTRIQ_URL}{case.CaseConcentriqId}"
        )

    caseStaffs = db.query(VCaseStaff).filter(VCaseStaff.CaseId == caseId).all()

    interpreters = (
        db.query(VCaseInterpreter)
        .filter(VCaseInterpreter.CaseId == caseId)
        .all()
    )

    specimens = synoptic_specimen(caseId=caseId, db=db)
    specimenGroup = synoptic_specimen_group(caseId=caseId, db=db)

    result = {
        "case": case,
        "caseComments": [],
        "caseStaffs": [],
        "interpreters": [],
        "specimens": specimens,
        "specimensGroup": specimenGroup,
    }

    #     for row in caseComments:
    #          result["caseComments"].append(row2dict(row))

    for row in caseStaffs:
        result["caseStaffs"].append(row2dict(row))

    for row in interpreters:
        result["interpreters"].append(row2dict(row))

    return result


def get_mrn_casenumber_view(casenumber: str, db: Session):
    case = db.query(VCaseMrn).filter(VCaseMrn.CaseNumber == casenumber).first()
    return case.PatientMrn if case is not None else None


def get_mrn_casenumber_select(casenumber: str, db: Session):
    stmt = select([VCaseMrn.PatientMrn]).where(
        VCaseMrn.CaseNumber == casenumber
    )
    case = db.execute(stmt).first()
    return case.PatientMrn if case is not None else None


def get_mrn_casenumber(casenumber: str, db: Session):
    sql = text(
        "SELECT TOP 1 PatientMrn "
        + "FROM dbo.V_Case_MRN "
        + f"WHERE CaseNumber = '{casenumber}'"
    )

    rs = db.execute(sql)
    for row in rs:
        return row[0]

    return None


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d
