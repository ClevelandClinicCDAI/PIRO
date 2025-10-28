from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Patient(Base):
    __tablename__ = "Patient"
    PatientId = Column(Integer, primary_key=True, index=True)
    GenderId = Column(Integer, ForeignKey("Gender.GenderId"), nullable=False)
    EthnicityId = Column(Integer, ForeignKey("Ethnicity.EthnicityId"), nullable=False)
    RaceId = Column(Integer, ForeignKey("Race.RaceId"), nullable=False)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    MiddleName = Column(String, nullable=False)
    DOB = Column(DateTime, nullable=False)
    MRN = Column(String, nullable=False)
    EpiId = Column(String, nullable=False)
    PatId = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    Gender = relationship("Gender", back_populates="Patient")
    Ethnicity = relationship("Ethnicity", back_populates="Patient")
    Race = relationship("Race", back_populates="Patient")
    Case = relationship("Case", back_populates="Patient")
