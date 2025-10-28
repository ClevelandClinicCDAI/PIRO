from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Case(Base):
    __tablename__ = "Case"
    CaseId = Column(Integer, primary_key=True, index=True)
    PatientId = Column(Integer, ForeignKey("Patient.PatientId"), nullable=False)
    HospitalId = Column(Integer, ForeignKey("Hospital.HospitalId"), nullable=False)
    CaseStatusId = Column(Integer, nullable=False)
    CaseTypeId = Column(Integer, nullable=False)
    SpecialtyId = Column(Integer, nullable=False)
    SpecimenYear = Column(Integer, nullable=False)
    # SpecimenNumber = Column(Integer, nullable=False)
    CaseNumber = Column(String, nullable=False)
    AccessionDate = Column(DateTime, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    Patient = relationship("Patient", back_populates="Case")
    Hospital = relationship("Hospital", back_populates="Case")
    Specimen = relationship("Specimen", back_populates="Case")
    TagCase = relationship("TagCase", back_populates="Case")
    CaseComment = relationship("CaseComment", back_populates="Case")
