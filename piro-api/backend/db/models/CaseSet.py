"""Fixed case membership and resumable, owner-specific review."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mssql import NVARCHAR
from db.base_class import Base

LongText = UnicodeText().with_variant(NVARCHAR(None), "mssql")


class CaseSet(Base):
    __tablename__ = "CaseSet"
    __table_args__ = (
        UniqueConstraint("OwnerId", "CreationKey", name="UQ_CaseSet_Creation"),
        Index("IX_CaseSet_Owner_Archived", "OwnerId", "Archived"),
        Index(
            "IX_CaseSet_Public_Specialty", "IsPublic", "Archived", "SpecialtyCategory"
        ),
        CheckConstraint(
            "IsPublic = 0 OR (SpecialtyCategory IS NOT NULL AND LTRIM(RTRIM(SpecialtyCategory)) <> '')",
            name="CK_CaseSet_PublicSpecialty",
        ),
        CheckConstraint(
            "SourceType IN ('SAVED_SEARCH','COHORT','OPERATION','MANUAL')",
            name="CK_CaseSet_Source",
        ),
        CheckConstraint(
            "CaptureState IN ('CAPTURING','READY','FAILED')", name="CK_CaseSet_Capture"
        ),
        CheckConstraint(
            "ReviewFilter IN ('ALL','UNREVIEWED','INCLUDED','EXCLUDED')",
            name="CK_CaseSet_Filter",
        ),
    )

    CaseSetId = Column(Integer, primary_key=True)
    OwnerId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    Name = Column(Unicode(250), nullable=False)
    Description = Column(Unicode(2000), nullable=False, default="", server_default="")
    SourceType = Column(String(20), nullable=False)
    # Retain source identities as provenance even if their source is later deleted.
    SourceId = Column(Integer, nullable=False)
    SourceName = Column(Unicode(1000), nullable=False)
    SourceQuery = Column(LongText, nullable=False, default="{}", server_default="{}")
    CreationKey = Column(String(36), nullable=False)
    CreationHash = Column(String(64), nullable=False)
    Archived = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    IsPublic = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    SpecialtyCategory = Column(Unicode(100), nullable=True)
    Revision = Column(Integer, nullable=False, default=0, server_default=text("0"))
    CreatedAt = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    UpdatedAt = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    CaptureState = Column(
        String(20), nullable=False, default="CAPTURING", server_default="CAPTURING"
    )
    CaptureCursor = Column(LongText, nullable=False, default="*", server_default="*")
    CaptureExpected = Column(Integer, nullable=True)
    CaptureSeen = Column(Integer, nullable=False, default=0, server_default=text("0"))
    CaptureFinishedAt = Column(DateTime, nullable=True)
    CaptureError = Column(Unicode(500), nullable=False, default="", server_default="")
    LastCaseId = Column(Integer, nullable=True)
    ReviewFilter = Column(
        String(20), nullable=False, default="ALL", server_default="ALL"
    )


class CaseSetCase(Base):
    __tablename__ = "CaseSetCase"
    __table_args__ = (
        UniqueConstraint("CaseSetId", "Ordinal", name="UQ_CaseSetCase_Ordinal"),
        Index("IX_CaseSetCase_Review_Order", "CaseSetId", "ReviewState", "Ordinal"),
        CheckConstraint(
            "ReviewState IN ('UNREVIEWED','INCLUDED','EXCLUDED')",
            name="CK_CaseSetCase_Review",
        ),
    )

    CaseSetId = Column(Integer, ForeignKey("CaseSet.CaseSetId"), primary_key=True)
    # No source-case FK: ETL/source deletion must not erase historical membership.
    CaseId = Column(Integer, primary_key=True)
    Ordinal = Column(Integer, nullable=False)
    ReviewState = Column(
        String(20), nullable=False, default="UNREVIEWED", server_default="UNREVIEWED"
    )
    ReviewedAt = Column(DateTime, nullable=True)
    ReviewerId = Column(Integer, nullable=True)
    Revision = Column(Integer, nullable=False, default=0, server_default=text("0"))


class CaseSetSpecimen(Base):
    """Selected specimens for one case membership, independent of other sets."""

    __tablename__ = "CaseSetSpecimen"
    __table_args__ = (
        ForeignKeyConstraint(
            ["CaseSetId", "CaseId"],
            ["CaseSetCase.CaseSetId", "CaseSetCase.CaseId"],
            name="FK_CaseSetSpecimen_Member",
            ondelete="CASCADE",
        ),
    )

    CaseSetId = Column(Integer, primary_key=True)
    CaseId = Column(Integer, primary_key=True)
    # Retain selections if ETL later removes a clinical specimen.
    SpecimenId = Column(Integer, primary_key=True)
    SpecimenNumber = Column(Unicode(100), nullable=False)
    SelectedBy = Column(Integer, nullable=False)
    SelectedAt = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )
