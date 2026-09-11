import os

os.environ.setdefault("DATABASE", "SQLITE")

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apis.version1.route_extraction import _require_session_read_access
from db.base_class import Base
from db.models.ExtractionSession import ExtractionSession
from db.models.SearchRequest import SearchRequest
from db.models.User import User


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            ExtractionSession.__table__,
            SearchRequest.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def _create_user(db, nuid: str) -> User:
    user = User(
        NUID=nuid,
        FirstName="Test",
        LastName="User",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_session(db, owner_id: int, name: str) -> ExtractionSession:
    session = ExtractionSession(
        UserId=owner_id,
        Name=name,
        Status="running",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _create_search_request(
    db,
    requester_id: int,
    session_id: int,
    approved_by_id: int | None = None,
) -> SearchRequest:
    search_request = SearchRequest(
        RequesterId=requester_id,
        ExtractionSessionId=session_id,
        IsLlmAssisted=True,
        SearchRequestStatusId=1,
        SearchRequestReasonId=1,
        RequestName="Extraction request",
        ApprovedById=approved_by_id,
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(search_request)
    db.commit()
    db.refresh(search_request)
    return search_request


def test_require_session_read_access_allows_linked_approver(db):
    owner = _create_user(db, "extraction-owner@example.com")
    approver = _create_user(db, "extraction-approver@example.com")
    session = _create_session(db, owner.UserId, "approver-readable-session")
    _create_search_request(db, owner.UserId, session.ExtractionSessionId, approver.UserId)

    result = _require_session_read_access(
        session.ExtractionSessionId,
        approver.UserId,
        db,
    )

    assert result.ExtractionSessionId == session.ExtractionSessionId


def test_require_session_read_access_denies_unrelated_user(db):
    owner = _create_user(db, "extraction-owner-2@example.com")
    approver = _create_user(db, "extraction-approver-2@example.com")
    outsider = _create_user(db, "extraction-outsider@example.com")
    session = _create_session(db, owner.UserId, "outsider-blocked-session")
    _create_search_request(db, owner.UserId, session.ExtractionSessionId, approver.UserId)

    with pytest.raises(HTTPException) as exc:
        _require_session_read_access(
            session.ExtractionSessionId,
            outsider.UserId,
            db,
        )

    assert exc.value.status_code == 403


def test_require_session_read_access_denies_admin_without_linked_request(db):
    owner = _create_user(db, "extraction-owner-3@example.com")
    admin = _create_user(db, "extraction-admin@example.com")
    session = _create_session(db, owner.UserId, "admin-scoped-session")

    with pytest.raises(HTTPException) as exc:
        _require_session_read_access(
            session.ExtractionSessionId,
            admin.UserId,
            db,
        )

    assert exc.value.status_code == 403
