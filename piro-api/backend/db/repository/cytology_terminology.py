from core.constants import Constants
from db.models.CytologyTerminology import CytologyTerminology
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.cytology_evaluation import CytologyTerminologyVM


def _values_for_category(db: Session, category: str) -> list[str]:
    rows = (
        db.query(CytologyTerminology)
        .filter(CytologyTerminology.Category == category)
        .filter(CytologyTerminology.IsActive == True)  # noqa: E712
        .order_by(asc(CytologyTerminology.SortOrder))
        .all()
    )
    return [row.Value for row in rows]


def get_cytology_terminology(db: Session) -> CytologyTerminologyVM:
    """Returns every categorical dropdown list required by the cytology
    evaluation form, sourced from the CytologyTerminology table (seeded from
    temp/terminologies.xlsx). Values are never invented here."""
    return CytologyTerminologyVM(
        procedureType=_values_for_category(
            db, Constants.CytologyTerminologyCategory.PROCEDURE_TYPE.value
        ),
        readLocation=_values_for_category(
            db, Constants.CytologyTerminologyCategory.READ_LOCATION.value
        ),
        procedureLocation=_values_for_category(
            db, Constants.CytologyTerminologyCategory.PROCEDURE_LOCATION.value
        ),
        site=_values_for_category(
            db, Constants.CytologyTerminologyCategory.SITE.value
        ),
        adequacy=_values_for_category(
            db, Constants.CytologyTerminologyCategory.ADEQUACY.value
        ),
    )


def is_valid_terminology_value(
    db: Session, category: str, value: str | None
) -> bool:
    if value is None:
        return True
    return (
        db.query(CytologyTerminology)
        .filter(CytologyTerminology.Category == category)
        .filter(CytologyTerminology.Value == value)
        .filter(CytologyTerminology.IsActive == True)  # noqa: E712
        .first()
        is not None
    )
