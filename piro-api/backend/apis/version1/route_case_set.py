from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import (
    get_current_user_id,
    get_current_user_role,
    get_current_user_attest,
)
from db.repository import case_set
from db.session import get_db, get_solr
from viewmodel.case_set import (
    CaseSetCapture,
    CaseSetCreate,
    CaseSetAddCases,
    CaseSetCartCreate,
    CaseSetDecision,
    CaseSetEdit,
    CaseSetSharing,
    CaseSetPosition,
    CaseSetSpecimenSelection,
    CaseSetOperationCreate,
    CaseSetOperationPreview,
    ReviewFilter,
)


def configured_database(db=Depends(get_db)):
    case_set.require_schema(db)
    return db


router = APIRouter(
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
    ]
)
Database = Annotated[object, Depends(configured_database)]
Owner = Annotated[int, Depends(get_current_user_id)]


@router.get("/sources")
def sources(owner: Owner, db: Database):
    return case_set.sources(owner, db)


@router.get("/specialty-categories")
def specialty_categories(owner: Owner, db: Database):
    return case_set.specialty_categories(db)


@router.get("")
def list_sets(
    owner: Owner,
    db: Database,
    archived: bool = False,
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
):
    return case_set.list_sets(owner, archived, page, size, db)


@router.post("", status_code=201)
def create(payload: CaseSetCreate, owner: Owner, db: Database):
    return case_set.create(owner, payload, db)


@router.get("/operations/sources")
def operation_sources(owner: Owner, db: Database):
    return case_set.operation_sources(owner, db)


@router.post("/operations/preview")
def preview_operation(payload: CaseSetOperationPreview, owner: Owner, db: Database):
    return case_set.preview_operation(owner, payload, db)


@router.post("/operations", status_code=201)
def create_operation(payload: CaseSetOperationCreate, owner: Owner, db: Database):
    return case_set.create_operation(owner, payload, db)


@router.get("/cart/targets")
def cart_targets(owner: Owner, db: Database):
    return case_set.addition_targets(owner, db)


@router.post("/from-cart", status_code=201)
def create_from_cart(
    payload: CaseSetCartCreate, owner: Owner, db: Database, solr=Depends(get_solr)
):
    return case_set.create_from_cart(owner, payload, db, solr)


@router.post("/{set_id}/cases")
def add_cases(
    set_id: int,
    payload: CaseSetAddCases,
    owner: Owner,
    db: Database,
    solr=Depends(get_solr),
):
    return case_set.add_cases(set_id, owner, payload, db, solr)


@router.get("/{set_id}")
def detail(set_id: int, owner: Owner, db: Database):
    return case_set.summary(case_set.owned(set_id, owner, db), db)


@router.put("/{set_id}")
def edit(set_id: int, payload: CaseSetEdit, owner: Owner, db: Database):
    return case_set.edit(set_id, owner, payload, db)


@router.put("/{set_id}/sharing")
def sharing(set_id: int, payload: CaseSetSharing, owner: Owner, db: Database):
    return case_set.share(set_id, owner, payload, db)


@router.delete("/{set_id}", status_code=204)
def delete_set(
    set_id: int, owner: Owner, db: Database, revision: int = Query(..., ge=0)
):
    case_set.delete_set(set_id, owner, revision, db)
    return Response(status_code=204)


@router.post("/{set_id}/capture")
def capture(
    set_id: int,
    payload: CaseSetCapture,
    owner: Owner,
    db: Database,
    solr=Depends(get_solr),
):
    return case_set.capture(set_id, owner, payload.cursor, db, solr)


@router.get("/{set_id}/cases")
def members(
    set_id: int,
    owner: Owner,
    db: Database,
    role: Annotated[str, Depends(get_current_user_role)],
    attest: Annotated[bool, Depends(get_current_user_attest)],
    filter: ReviewFilter = "ALL",
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),
    resume: bool = False,
    solr=Depends(get_solr),
):
    return case_set.members(
        set_id, owner, filter, page, size, resume, role, attest, db, solr
    )


@router.put("/{set_id}/cases/{case_id}")
def decide(
    set_id: int, case_id: int, payload: CaseSetDecision, owner: Owner, db: Database
):
    return case_set.decide(set_id, case_id, owner, payload, db)


@router.put("/{set_id}/position")
def position(set_id: int, payload: CaseSetPosition, owner: Owner, db: Database):
    return case_set.position(set_id, owner, payload, db)


@router.get("/{set_id}/cases/{case_id}/specimens")
def specimens(set_id: int, case_id: int, owner: Owner, db: Database):
    return case_set.specimens(set_id, case_id, owner, db)


@router.put("/{set_id}/cases/{case_id}/specimens")
def select_specimens(
    set_id: int,
    case_id: int,
    payload: CaseSetSpecimenSelection,
    owner: Owner,
    db: Database,
):
    return case_set.select_specimens(set_id, case_id, owner, payload, db)
