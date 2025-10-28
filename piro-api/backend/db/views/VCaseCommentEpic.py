from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String


class VCaseCommentEpic(Base):
    __tablename__ = "V_CaseCommentEpic"
    Id = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, nullable=False)
    CommentTypeId = Column(Integer, nullable=False)
    CommentType = Column(String, nullable=False)
    CommentText = Column(String, nullable=False)
    SourceCommentType = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True))
    UpdateDate = Column(DateTime(timezone=True), nullable=True)
