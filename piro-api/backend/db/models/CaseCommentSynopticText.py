from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class CaseCommentSynopticText(Base):
    __tablename__ = "CaseCommentSynopticText"
    Id = Column(Integer, primary_key=True, index=True)
    SynopticId = Column(Integer, nullable=False)
    Name = Column(String, nullable=False)
    ResultId = Column(Integer, nullable=False)
    HlvId = Column(String, nullable=False)
    DataType = Column(String, nullable=False)
    ContextName = Column(String, nullable=False)
    ContexHierarchy = Column(String, nullable=False)
    ValueLine = Column(String, nullable=False)
    Level1 = Column(String, nullable=False)
    Level2 = Column(String, nullable=False)
    Level3 = Column(String, nullable=False)
    Level4 = Column(String, nullable=False)
    Level5 = Column(String, nullable=False)
    Level6 = Column(String, nullable=False)
    ElementName = Column(String, nullable=False)
    ElementValue = Column(String, nullable=False)
    SynopticKey = Column(String, nullable=False)
    ElementComment = Column(String, nullable=False)
    CommentLine = Column(Integer, nullable=False)
    CommentSequence = Column(Integer, nullable=False)
    RefSynopticKey = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
