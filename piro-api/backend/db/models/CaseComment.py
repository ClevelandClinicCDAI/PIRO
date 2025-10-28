from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class CaseComment(Base):
    __tablename__ = "CaseComment"
    CaseCommentId = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    CommentTypeId = Column(
        Integer, ForeignKey("CommentType.CommentTypeId"), nullable=False
    )
    Text = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    Case = relationship("Case", back_populates="CaseComment")
    CommentType = relationship("CommentType", back_populates="CaseComment")
