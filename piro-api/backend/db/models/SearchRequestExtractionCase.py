from db.base_class import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class SearchRequestExtractionCase(Base):
    __tablename__ = "SearchRequestExtractionCase"
    __table_args__ = (
        UniqueConstraint(
            "SearchRequestId",
            "ExtractionRunId",
            "CaseId",
            name="uq_search_request_extraction_case_request_run_case",
        ),
    )

    SearchRequestExtractionCaseId = Column(
        Integer, primary_key=True, index=True
    )
    SearchRequestId = Column(
        Integer,
        ForeignKey("SearchRequest.SearchRequestId"),
        nullable=False,
    )
    ExtractionRunId = Column(
        Integer,
        ForeignKey("ExtractionRun.ExtractionRunId"),
        nullable=False,
    )
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    SortOrder = Column(Integer, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String(255), nullable=False)

    SearchRequest = relationship(
        "SearchRequest", foreign_keys=[SearchRequestId]
    )
    ExtractionRun = relationship(
        "ExtractionRun", foreign_keys=[ExtractionRunId]
    )
    Case = relationship("Case", foreign_keys=[CaseId])
