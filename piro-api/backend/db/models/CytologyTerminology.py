from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class CytologyTerminology(Base):
    __tablename__ = "CytologyTerminology"
    CytologyTerminologyId = Column(Integer, primary_key=True, index=True)
    Category = Column(String, nullable=False, index=True)
    Value = Column(String, nullable=False)
    SortOrder = Column(Integer, nullable=False, default=0)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
