from db.models.Patient import Patient
from sqlalchemy.orm import Session
from sqlalchemy import asc


def search_mrn(mrn: str, db: Session):
    patients = (
        db.query(Patient)
        .filter(Patient.IsActive == True)  # noqa
        .filter(Patient.MRN == mrn)  # noqa
        .order_by(asc(Patient.FirstName))
        .all()
    )
    return patients
