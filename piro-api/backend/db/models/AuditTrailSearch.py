from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AuditTrailSearch(Base):
    __tablename__ = "AuditTrailSearch"
    AuditTrailSearchId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    SearchQuery = Column(String, nullable=False)
    SearchDisplay = Column(String, nullable=False)
    SearchUrl = Column(String, nullable=False)
    AdvancedQuery = Column(String, nullable=True)
    MRN = Column(String, nullable=True)
    TotalHits = Column(Integer, nullable=False)
    ExecutionTime = Column(Numeric(18, 6), nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    # User = relationship("User", back_populates="AuditTrailSearch")
    AuditTrailCase = relationship(
        "AuditTrailCase", back_populates="AuditTrailSearch"
    )
