from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class AnnotationConfiguration(Base):
    __tablename__ = "AnnotationConfiguration"
    AnnotationConfigurationId = Column(Integer, primary_key=True, index=True)
    AnnotationMetric = Column(String, nullable=False)
    DisplayText = Column(String, nullable=False)
    DataParseProperty = Column(String, nullable=False)
    UIModel = Column(String, nullable=False)
    RowIndex = Column(Integer, nullable=False)
    ColumnIndex = Column(Integer, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
