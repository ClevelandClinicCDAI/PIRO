"""Read-only teaching sets for all authenticated PIRO users."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from apis.version1.route_case_set import configured_database
from core.auth_bearer import JWTBearer
from core.security_user import (
    get_current_user_id,
    get_current_user_role,
    get_current_user_attest,
)
from db.models.User import User
from db.repository import case_set
from db.session import get_solr

Database = Annotated[object, Depends(configured_database)]


def active_viewer(
    response: Response,
    db: Database,
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    response.headers["Cache-Control"] = "no-store"
    if (
        db.query(User.UserId)
        .filter(User.UserId == user_id, User.IsActive == True)
        .first()
        is None
    ):  # noqa: E712
        raise HTTPException(403, "An active PIRO account is required.")


router = APIRouter(dependencies=[Depends(JWTBearer()), Depends(active_viewer)])


@router.get("")
def browse(
    db: Database,
    specialty: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
):
    return case_set.teaching_sets(specialty, page, size, db)


@router.get("/{set_id}")
def detail(set_id: int, db: Database):
    return case_set.teaching_summary(case_set.teaching_set(set_id, db), db)


@router.get("/{set_id}/cases")
def members(
    set_id: int,
    db: Database,
    role: Annotated[str, Depends(get_current_user_role)],
    attest: Annotated[bool, Depends(get_current_user_attest)],
    page: int = Query(1, ge=1),
    size: int = Query(1, ge=1, le=50),
    solr=Depends(get_solr),
):
    return case_set.teaching_members(set_id, page, size, role, attest, db, solr)
