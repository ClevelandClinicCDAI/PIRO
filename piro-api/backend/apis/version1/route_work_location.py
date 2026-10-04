from core.auth_bearer import JWTBearer
from core.constants import Constants
from db.repository.work_location import create_login_event
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.workLocation import (
    WorkLocationIngestResult,
    WorkLocationLoginEventCreate,
)

router = APIRouter()


@router.post(
    "/events",
    dependencies=[Depends(JWTBearer([Constants.RoleWorkLocationIngest]))],
    response_model=WorkLocationIngestResult,
)
async def ingest_login_event(
    event: WorkLocationLoginEventCreate,
    db: Session = Depends(get_db),
):
    row, duplicate = create_login_event(event, db)
    return {
        "accepted": True,
        "duplicate": duplicate,
        "event_id": row.EventId,
    }
