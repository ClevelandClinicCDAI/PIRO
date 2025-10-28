from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class SearchRequestDataField(Base):
    __tablename__ = "SearchRequestDataField"
    SearchRequestDataFieldId = Column(Integer, primary_key=True, index=True)
    SearchRequestId = Column(Integer, nullable=False)
    DataFieldId = Column(Integer, nullable=False)
    IsSelected = Column(Boolean, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
