import os

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base_class import Base
from db.models.Case import Case
from db.models.ExtractionResult import ExtractionResult
from db.models.ExtractionRun import ExtractionRun
from db.models.ExtractionSession import ExtractionSession
from db.models.User import User
from db.repository.extraction import (
    clone_results_for_run,
    create_run,
    create_session,
    get_results_for_run,
    get_results_for_session,
    upsert_result,
)

os.environ.setdefault("DATABASE", "SQLITE")


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Case.__table__,
            ExtractionSession.__table__,
            ExtractionRun.__table__,
            ExtractionResult.__table__,
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


def test_retry_run_keeps_previous_successes_and_original_run_sees_retry_result(
    db,
):
    user = _create_user(db, "retry-user@example.com")
    case_a = _create_case(db, "CASE-A")
    case_b = _create_case(db, "CASE-B")

    session = create_session(
        name="retry-session",
        user_id=user.UserId,
        user="pytest",
        db=db,
    )
    original_run = create_run(
        session_id=session.ExtractionSessionId,
        schema_json='{"field": "string"}',
        llm_provider="ollama",
        llm_model="llama3.2",
        user="pytest",
        db=db,
    )

    upsert_result(
        run_id=original_run.ExtractionRunId,
        session_id=session.ExtractionSessionId,
        case_id=case_a.CaseId,
        field_name="field_a",
        extracted_value="alpha",
        confidence=0.91,
        provenance_text="case a provenance",
        source_comment_id=None,
        provenance_start=None,
        provenance_end=None,
        user="pytest",
        db=db,
    )

    retry_run = create_run(
        session_id=session.ExtractionSessionId,
        schema_json='{"field": "string"}',
        llm_provider="ollama",
        llm_model="llama3.2",
        user="pytest",
        db=db,
        run_type="retry",
    )

    clone_results_for_run(
        source_run_id=original_run.ExtractionRunId,
        destination_run_id=retry_run.ExtractionRunId,
        user="pytest",
        db=db,
    )

    upsert_result(
        run_id=retry_run.ExtractionRunId,
        session_id=session.ExtractionSessionId,
        case_id=case_b.CaseId,
        field_name="field_b",
        extracted_value="bravo",
        confidence=0.93,
        provenance_text="case b provenance",
        source_comment_id=None,
        provenance_start=None,
        provenance_end=None,
        user="pytest",
        db=db,
        related_run_ids=[original_run.ExtractionRunId],
    )

    session_results = get_results_for_session(session.ExtractionSessionId, db)
    assert [
        (r.CaseId, r.FieldName, r.ExtractionRunId) for r in session_results
    ] == [
        (case_a.CaseId, "field_a", retry_run.ExtractionRunId),
        (case_b.CaseId, "field_b", retry_run.ExtractionRunId),
    ]

    original_results = get_results_for_run(original_run.ExtractionRunId, db)
    assert {(r.CaseId, r.FieldName) for r in original_results} == {
        (case_a.CaseId, "field_a"),
        (case_b.CaseId, "field_b"),
    }
