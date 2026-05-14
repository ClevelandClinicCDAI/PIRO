from core.auth_bearer import JWTBearer
from db.repository.synopticBrowser import get_synoptic_protocols, get_synoptic_tnm_facets
from db.session import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/protocols", dependencies=[Depends(JWTBearer())])
async def read_protocols(db: Session = Depends(get_db)):
    return get_synoptic_protocols(db=db)


@router.get("/tnmfacets", dependencies=[Depends(JWTBearer())])
async def read_tnm_facets(
    protocol: str = Query(..., description="Cancer protocol name"),
    db: Session = Depends(get_db),
):
    return get_synoptic_tnm_facets(protocol=protocol, db=db)
