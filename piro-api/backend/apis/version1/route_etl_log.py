from core.auth_bearer import JWTBearer
from db.repository.etl_log import list_log_month
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.etl_log import ETL_LogVM

router = APIRouter()


@router.get(
    "/days30",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[ETL_LogVM],
)
async def list_log_30(db: Session = Depends(get_db)):
    logs = list_log_month(30, db=db)
    return paginate(logs)


@router.get(
    "/days60",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[ETL_LogVM],
)
async def list_log_60(db: Session = Depends(get_db)):
    logs = list_log_month(60, db=db)
    return paginate(logs)


@router.get(
    "/days90",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[ETL_LogVM],
)
async def list_log_90(db: Session = Depends(get_db)):
    logs = list_log_month(90, db=db)
    return paginate(logs)
