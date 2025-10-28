from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AuditTrailCase(Base):
    __tablename__ = "AuditTrailCase"
    AuditTrailCaseId = Column(Integer, primary_key=True, index=True)
    AuditTrailSearchId = Column(
        Integer,
        ForeignKey("AuditTrailSearch.AuditTrailSearchId"),
        nullable=False,
    )
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    AuditTrailSearch = relationship(
        "AuditTrailSearch", back_populates="AuditTrailCase"
    )
    # User = relationship("User", back_populates="AuditTrailCase")
    # Case = relationship("Case", back_populates="AuditTrailCase")
