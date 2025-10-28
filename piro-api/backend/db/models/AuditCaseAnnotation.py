from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class AuditCaseAnnotation(Base):
    __tablename__ = "AuditCaseAnnotation"
    AuditCaseAnnotationId = Column(Integer, primary_key=True, index=True)
    CaseAnnotationId = Column(Integer, nullable=False)
    AnnotationId = Column(Integer, nullable=False)
    CaseId = Column(Integer, nullable=False)
    AnnotationConfigurationId = Column(Integer, nullable=False)
    ModelName = Column(String, nullable=False)
    AnnotationValue = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
