from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class CohortCase(Base):
    __tablename__ = "CohortCase"
    CohortCaseId = Column(Integer, primary_key=True, index=True)
    CohortPatientId = Column(Integer, nullable=True)
    CohortId = Column(Integer, nullable=False)
    PatientId = Column(Integer, nullable=True)
    CaseNumber = Column(String, nullable=True)
    CaseId = Column(Integer, nullable=True)
    IsActive = Column(Boolean, nullable=False)
    LoadType = Column(String, nullable=False)
    IsSolrUpdated = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
