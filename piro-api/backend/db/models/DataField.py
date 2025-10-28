from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class DataField(Base):
    __tablename__ = "DataField"
    DataFieldId = Column(Integer, primary_key=True, index=True)
    DataFieldCategoryId = Column(Integer, nullable=False)
    DisplayName = Column(String, nullable=False)
    Code = Column(String, nullable=False)
    SolrField = Column(String, nullable=False)
    Sequence = Column(Integer, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
