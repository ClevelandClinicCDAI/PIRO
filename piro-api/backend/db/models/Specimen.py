from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Specimen(Base):
    __tablename__ = "Specimen"
    SpecimenId = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    SpecimenSourceId = Column(
        Integer, ForeignKey("SpecimenSource.SpecimenSourceId"), nullable=False
    )
    SpecimenTypeId = Column(
        Integer, ForeignKey("SpecimenType.SpecimenTypeId"), nullable=False
    )
    FormatNumber = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    SpecimenSource = relationship("SpecimenSource", back_populates="Specimen")
    SpecimenType = relationship("SpecimenType", back_populates="Specimen")
    Case = relationship("Case", back_populates="Specimen")
