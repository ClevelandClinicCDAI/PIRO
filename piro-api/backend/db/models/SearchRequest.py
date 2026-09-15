from db.base_class import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class SearchRequest(Base):
    __tablename__ = "SearchRequest"
    SearchRequestId = Column(Integer, primary_key=True, index=True)
    RequesterId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    # Exactly one of SearchId / ExtractionSessionId is populated: a request is
    # either sourced from a Saved Search, or from an LLM-assisted Structured
    # Data Extraction schema (see IsLlmAssisted).
    SearchId = Column(Integer, ForeignKey("Search.SearchId"), nullable=True)
    ExtractionSessionId = Column(
        Integer, ForeignKey("ExtractionSession.ExtractionSessionId"), nullable=True
    )
    ExtractionRunId = Column(
        Integer, ForeignKey("ExtractionRun.ExtractionRunId"), nullable=True
    )
    IsLlmAssisted = Column(Boolean, nullable=False, default=False)
    SearchRequestStatusId = Column(
        Integer,
        ForeignKey("SearchRequestStatus.SearchRequestStatusId"),
        nullable=False,
    )
    SearchRequestReasonId = Column(Integer, nullable=False)
    RequestName = Column(String, nullable=True)
    FromDate = Column(DateTime(timezone=True), nullable=True)
    ToDate = Column(DateTime(timezone=True), nullable=True)
    IRB = Column(String, nullable=True)
    IsPediatric = Column(Boolean, nullable=True)
    RequestDocumentFile = Column(LargeBinary, nullable=True)
    RequestDocumentName = Column(String, nullable=True)
    RequestDocumentSize = Column(Float, nullable=True)
    RequestDocumentType = Column(String, nullable=True)
    RequestDocumentExtension = Column(String, nullable=True)
    RequestComment = Column(String, nullable=True)
    ResultDocumentFile = Column(LargeBinary, nullable=True)
    ResultDocumentName = Column(String, nullable=True)
    ResultDocumentSize = Column(Float, nullable=True)
    ApprovedById = Column(Integer, nullable=True)
    ApprovedDate = Column(DateTime(timezone=True), nullable=True)
    ApprovalComment = Column(String, nullable=True)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    User = relationship("User", back_populates="SearchRequest")
    Search = relationship("Search", back_populates="SearchRequest")
    ExtractionSession = relationship("ExtractionSession", foreign_keys=[ExtractionSessionId])
    ExtractionRun = relationship("ExtractionRun", foreign_keys=[ExtractionRunId])
    SearchRequestStatus = relationship(
        "SearchRequestStatus", back_populates="SearchRequest"
    )
