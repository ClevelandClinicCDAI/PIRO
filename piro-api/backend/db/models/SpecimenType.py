from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class SpecimenType(Base):
    __tablename__ = "SpecimenType"
    SpecimenTypeId = Column(Integer, primary_key=True, index=True)
    ShortName = Column(String, nullable=False)
    Code = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    # Category = Column(String, nullable=False)
    DataLabReference = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    # Case = relationship("Case", back_populates="SpecimenType")
    Specimen = relationship("Specimen", back_populates="SpecimenType")
