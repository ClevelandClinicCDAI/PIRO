from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class AnnotationCaseFeedback(Base):
    __tablename__ = "AnnotationCaseFeedback"
    AnnotationCaseFeedbackId = Column(Integer, primary_key=True, index=True)
    AnnotationConfigurationId = Column(Integer, nullable=False)
    CaseId = Column(Integer, nullable=False)
    UserId = Column(Integer, nullable=False)
    Feedback = Column(String, nullable=False)
    Comment = Column(String, nullable=False)
    IsReviewed = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
