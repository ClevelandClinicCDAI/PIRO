from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class AuditTrailCaseInfo(Base):
    __tablename__ = "AuditTrailCaseInfo"
    AuditTrailCaseInfoId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    CaseId = Column(Integer, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
