import asyncio
import os
from pathlib import Path

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base_class import Base
from db.models.Case import Case
from db.models.ExtractionQueue import ExtractionQueue
from db.models.ExtractionResult import ExtractionResult  # noqa: F401
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.models.Search import Search  # noqa: F401
from db.models.SearchRequest import SearchRequest
from db.models.SearchRequestExtractionCase import SearchRequestExtractionCase
from db.models.SearchRequestReason import SearchRequestReason  # noqa: F401
from db.models.SearchRequestStatus import SearchRequestStatus  # noqa: F401
from db.models.User import User
from db.repository.searchRequest import (
    get_searchRequest_all,
    get_extraction_case_ids_for_request,
    snapshot_extraction_cases_for_request,
)
from apis.version1 import route_searchRequest

os.environ.setdefault("DATABASE", "SQLITE")


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Case.__table__,
            Search.__table__,
            SearchRequestStatus.__table__,
            SearchRequest.__table__,
            ExtractionSession.__table__,
            ExtractionRun.__table__,
            ExtractionQueue.__table__,
            SearchRequestExtractionCase.__table__,
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


def _create_case(db, case_number: str) -> Case:
    case = Case(
        PatientId=1,
        HospitalId=1,
        CaseStatusId=1,
        CaseTypeId=1,
        SpecialtyId=1,
        SpecimenYear=2026,
        CaseNumber=case_number,
        AccessionDate=datetime(2026, 1, 1),
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def _create_session(db, owner_id: int) -> ExtractionSession:
    session = ExtractionSession(
        UserId=owner_id,
        Name="snapshot-session",
        SchemaJson='{"field": "string"}',
        Status="draft",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _create_run(db, session_id: int) -> ExtractionRun:
    run = ExtractionRun(
        ExtractionSessionId=session_id,
        SchemaJson='{"field": "string"}',
        LlmProvider="ollama",
        LlmModel="llama3.2",
        Status="completed_with_errors",
        RunType="full",
        CreateBy="pytest",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _create_request(
    db, requester_id: int, session_id: int, run_id: int
) -> SearchRequest:
    request = SearchRequest(
        RequesterId=requester_id,
        SearchId=None,
        ExtractionSessionId=session_id,
        ExtractionRunId=run_id,
        IsLlmAssisted=True,
        SearchRequestStatusId=1,
        SearchRequestReasonId=1,
        RequestName="snapshot-request",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def test_request_extraction_case_snapshot_preserves_original_membership(db):
    user = _create_user(db, "snapshot-user@example.com")
    case_a = _create_case(db, "CASE-A")
    case_b = _create_case(db, "CASE-B")
    case_c = _create_case(db, "CASE-C")
    session = _create_session(db, user.UserId)
    run = _create_run(db, session.ExtractionSessionId)
    request = _create_request(
        db,
        requester_id=user.UserId,
        session_id=session.ExtractionSessionId,
        run_id=run.ExtractionRunId,
    )

    snapshot_extraction_cases_for_request(
        searchRequestId=request.SearchRequestId,
        extractionRunId=run.ExtractionRunId,
        case_ids=[case_a.CaseId, case_b.CaseId],
        user="pytest",
        db=db,
    )

    db.add(
        ExtractionQueue(
            ExtractionSessionId=session.ExtractionSessionId,
            CaseId=case_c.CaseId,
            Status="pending",
            AttemptCount=0,
            CreateBy="pytest",
        )
    )
    db.commit()

    assert get_extraction_case_ids_for_request(
        searchRequestId=request.SearchRequestId,
        extractionRunId=run.ExtractionRunId,
        db=db,
    ) == [case_a.CaseId, case_b.CaseId]


def test_extraction_request_without_search_can_be_downloaded(db, monkeypatch):
    user = _create_user(db, "extraction-download@example.com")
    session = _create_session(db, user.UserId)
    request = _create_request(
        db, user.UserId, session.ExtractionSessionId, None
    )
    request.SearchRequestStatusId = 2
    request.RequestDocumentFile = b"IRB attachment"
    request.RequestDocumentName = "irb"
    request.RequestDocumentExtension = ".pdf"
    request.RequestDocumentType = "application/pdf"
    db.add(
        SearchRequestStatus(
            SearchRequestStatusId=2,
            ShortName="Submitted",
            Code="SUBMIT",
            Description="Submitted",
            IsActive=True,
            CreateBy="pytest",
        )
    )
    db.commit()

    found = get_searchRequest_all(request.SearchRequestId, db)
    assert found.SearchId is None
    assert found.SearchName is None
    assert found.ExtractionSessionId == session.ExtractionSessionId
    assert found.IsLlmAssisted is True
    assert found.RequestDocumentFile == b"IRB attachment"

    monkeypatch.setattr(
        route_searchRequest,
        "create_audit_search_request",
        lambda **kwargs: None,
    )
    response = asyncio.run(
        route_searchRequest.download(
            request.SearchRequestId, user.NUID, user.UserId, db
        )
    )
    try:
        assert Path(response.path).read_bytes() == b"IRB attachment"
        assert response.media_type == "application/pdf"
    finally:
        Path(response.path).unlink()


def test_saved_search_request_keeps_search_name(db):
    user = _create_user(db, "saved-search-download@example.com")
    search = Search(
        UserId=user.UserId,
        Name="Saved cohort",
        Description="Saved cohort",
        SearchQuery="*:*",
        IsActive=True,
        CreateBy="pytest",
    )
    status = SearchRequestStatus(
        SearchRequestStatusId=2,
        ShortName="Submitted",
        Code="SUBMIT",
        Description="Submitted",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add_all([search, status])
    db.flush()
    request = SearchRequest(
        RequesterId=user.UserId,
        SearchId=search.SearchId,
        IsLlmAssisted=False,
        SearchRequestStatusId=status.SearchRequestStatusId,
        SearchRequestReasonId=1,
        RequestName="Saved search request",
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(request)
    db.commit()

    found = get_searchRequest_all(request.SearchRequestId, db)
    assert found.SearchId == search.SearchId
    assert found.SearchName == "Saved cohort"
    assert found.Requester == user.NUID
    assert found.SearchRequestStatus == "Submitted"
