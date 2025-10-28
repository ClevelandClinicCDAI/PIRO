from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class DataFieldCategory(Base):
    __tablename__ = "DataFieldCategory"
    DataFieldCategoryId = Column(Integer, primary_key=True, index=True)
    DisplayName = Column(String, nullable=False)
    Code = Column(String, nullable=False)
    Sequence = Column(Integer, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
