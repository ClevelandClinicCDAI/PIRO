from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Hospital(Base):
    __tablename__ = "Hospital"
    HospitalId = Column(Integer, primary_key=True, index=True)
    RegionId = Column(Integer, ForeignKey("Region.RegionId"), nullable=False)
    ShortName = Column(String, nullable=False)
    Code = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    DataLabReference = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    Region = relationship("Region", back_populates="Hospital")
    Case = relationship("Case", back_populates="Hospital")
