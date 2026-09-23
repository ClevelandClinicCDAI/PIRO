import os
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base_class import Base
from db.dict2Class import dict2Class
from db.models.Case import Case
from db.models.CaseCommentSynopticSpecimen import CaseCommentSynopticSpecimen
from db.views.VCaseCommentText import VCaseCommentText
import db.repository.extraction as extraction_mod
from db.repository.extraction import get_case_text_segments

os.environ.setdefault("DATABASE", "SQLITE")


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            Case.__table__,
            CaseCommentSynopticSpecimen.__table__,
            VCaseCommentText.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def _create_case(db, case_number: str, year: int) -> Case:
    case = Case(
        PatientId=1,
        HospitalId=1,
        CaseStatusId=1,
        CaseTypeId=1,
        SpecialtyId=1,
        SpecimenYear=year,
        CaseNumber=case_number,
        AccessionDate=datetime(year, 1, 1),
        IsActive=True,
        CreateBy="pytest",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def test_synoptic_prefers_parsed_synoptic_text_when_available(db):
    """When CaseCommentSynopticText has data for the case (recent cases),
    it is used instead of any legacy CaseComment-based synoptic text."""
    case = _create_case(db, "S24-1", 2024)
    db.add(
        CaseCommentSynopticSpecimen(
            CaseId=case.CaseId,
            SpecimenId=1,
            SynopticId=100,
            SynopticLine=1,
            CaseNum="S24-1",
            SpecimenNum="A1",
            RefSpecimenKey="k1",
            RefRequisitionKey="r1",
            CreateBy="pytest",
        )
    )
    # Legacy CaseComment-based synoptic text also happens to exist; it
    # should be ignored in favor of the parsed data.
    db.add(
        VCaseCommentText(
            Id=1,
            CaseId=case.CaseId,
            CommentTypeId=1,
            CommentType="Synoptic",
            CommentText="Stale legacy synoptic text",
            SourceCommentType="Synoptic",
        )
    )
    db.commit()

    fake_rows = [dict2Class({"Key": "Grade", "Value": "2"})]
    with patch.object(
        extraction_mod, "synoptic_report", return_value=fake_rows
    ):
        segments = get_case_text_segments(
            case.CaseId, db, comment_types={"synoptic"}
        )

    assert len(segments) == 1
    assert segments[0].CommentText == "Grade: 2"


def test_synoptic_falls_back_to_casecomment_when_no_parsed_data(db):
    """Older cases with no CaseCommentSynopticSpecimen/Text rows should
    fall back to the raw synoptic text stored on CaseComment."""
    case = _create_case(db, "S19-1", 2019)
    db.add(
        VCaseCommentText(
            Id=2,
            CaseId=case.CaseId,
            CommentTypeId=1,
            CommentType="Synoptic",
            CommentText="Legacy synoptic text from CaseComment",
            SourceCommentType="Synoptic",
        )
    )
    db.commit()

    segments = get_case_text_segments(
        case.CaseId, db, comment_types={"synoptic"}
    )

    assert len(segments) == 1
    assert segments[0].CommentText == "Legacy synoptic text from CaseComment"


def test_synoptic_returns_nothing_when_neither_source_has_data(db):
    case = _create_case(db, "S19-2", 2019)

    segments = get_case_text_segments(
        case.CaseId, db, comment_types={"synoptic"}
    )

    assert segments == []
