from typing import Annotated, List
from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.synopticBrowser import (
    get_synoptic_protocols,
    get_synoptic_tnm_facets,
    create_synoptic_cohort,
)
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


class SynopticFilterItem(BaseModel):
    key: str
    value: str


class SynopticTnmRequest(BaseModel):
    protocol: str
    filters: List[SynopticFilterItem] = []


class SynopticSaveCohortRequest(BaseModel):
    protocol: str
    filters: List[SynopticFilterItem] = []
    name: str
    description: str = ""


@router.get("/protocols", dependencies=[Depends(JWTBearer())])
async def read_protocols(db: Session = Depends(get_db)):
    return get_synoptic_protocols(db=db)


@router.post("/tnmfacets", dependencies=[Depends(JWTBearer())])
async def read_tnm_facets(
    body: SynopticTnmRequest,
    db: Session = Depends(get_db),
):
    filters = [{"key": f.key, "value": f.value} for f in body.filters]
    return get_synoptic_tnm_facets(protocol=body.protocol, filters=filters, db=db)


@router.post(
    "/savecohort",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def save_cohort(
    body: SynopticSaveCohortRequest,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    filters = [{"key": f.key, "value": f.value} for f in body.filters]
    cohort_id = create_synoptic_cohort(
        protocol=body.protocol,
        filters=filters,
        name=body.name,
        desc=body.description,
        user_id=current_user_id,
        user=current_user,
        db=db,
    )
    if cohort_id is None:
        raise HTTPException(status_code=404, detail="No matching cases found for this selection.")
    return {"cohort_id": cohort_id}
