from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func


class AuditTrailSearchRequest(Base):
    __tablename__ = "AuditTrailSearchRequest"
    AuditTrailSearchRequestId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    SearchRequestId = Column(Integer, nullable=False)
    Action = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
