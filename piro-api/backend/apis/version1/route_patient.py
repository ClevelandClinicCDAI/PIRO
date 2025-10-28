from typing import List

from core.auth_bearer import JWTBearer
from db.repository.patient import search_mrn
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.patient import PatientVM

router = APIRouter()


@router.get(
    "/search/{mrn}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[PatientVM],
)
async def get(mrn: str, db: Session = Depends(get_db)):
    patients = search_mrn(mrn=mrn, db=db)
    return patients
