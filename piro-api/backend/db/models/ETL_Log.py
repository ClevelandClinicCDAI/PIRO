from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class ETL_Log(Base):
    __tablename__ = "STG_ETL_PUSH_LOG"
    Id = Column(Integer, primary_key=True, index=True)
    TableName = Column(String, nullable=False)
    ToBeInsertRecordCount = Column(Integer, nullable=False)
    InsertRecordCount = Column(Integer, nullable=False)
    TobeUpdateRecordCount = Column(Integer, nullable=False)
    UpdateRecordCount = Column(Integer, nullable=False)
    IsSuccess = Column(Boolean, nullable=False)
    ErrorMessage = Column(String, nullable=False)
    CreatedDate = Column(DateTime(timezone=True), default=func.now())
    CreatedBy = Column(String, nullable=False)
