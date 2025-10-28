from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class CohortPatient(Base):
    __tablename__ = "CohortPatient"
    CohortPatientId = Column(Integer, primary_key=True, index=True)
    CohortId = Column(Integer, nullable=False)
    PatientId = Column(Integer, nullable=True)
    PatientMrn = Column(String, nullable=True)
    PatientEpi = Column(String, nullable=True)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
