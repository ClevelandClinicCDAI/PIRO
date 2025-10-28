from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class VSearchRequest(Base):
    __tablename__ = "V_SearchRequest"
    SearchRequestId = Column(Integer, primary_key=True, index=True)
    SearchId = Column(Integer, nullable=False)
    SearchRequestReasonId = Column(Integer, nullable=False)
    SearchRequestReason = Column(String, nullable=False)
    SearchRequestReasonCode = Column(String, nullable=False)
    RequestName = Column(String, nullable=False)
    FromDate = Column(DateTime(timezone=True), nullable=True)
    IRB = Column(String, nullable=True)
    IsPediatric = Column(Boolean, nullable=True)
    ToDate = Column(DateTime(timezone=True), nullable=True)
    RequesterId = Column(Integer, nullable=False)
    SearchRequestStatusId = Column(Integer, nullable=False)
    RequestName = Column(String, nullable=False)
    RequestDocumentExtension = Column(String, nullable=True)
    RequestComment = Column(String, nullable=True)
    ApprovedDate = Column(DateTime(timezone=True), nullable=True)
    ApprovalComment = Column(String, nullable=True)
    IsActive = Column(Boolean, nullable=False)
    SearchName = Column(String, nullable=False)
    SearchRequestStatus = Column(String, nullable=False)
    RequestedBy = Column(String, nullable=False)
    ApprovedBy = Column(String, nullable=True)
    CreateDate = Column(DateTime(timezone=True), nullable=True)
    UpdateDate = Column(DateTime(timezone=True), nullable=True)
