from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class CytologyEvaluationSite(Base):
    __tablename__ = "CytologyEvaluationSite"
    CytologyEvaluationSiteId = Column(Integer, primary_key=True, index=True)
    CytologyEvaluationId = Column(
        Integer, ForeignKey("CytologyEvaluation.CytologyEvaluationId"), nullable=False
    )
    Site = Column(String, nullable=True)
    EvalEpisodeNumber = Column(Integer, nullable=True)
    Adequacy = Column(String, nullable=True)
    DQCount = Column(Integer, nullable=False, default=0)
    PapCount = Column(Integer, nullable=False, default=0)
    ThinPrepCount = Column(Integer, nullable=False, default=0)
    CellBlockCount = Column(Integer, nullable=False, default=0)
    UnstainedSlidesCount = Column(Integer, nullable=False, default=0)
    SortOrder = Column(Integer, nullable=False, default=0)
    CreateDate = Column(DateTime(timezone=False), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=False), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)

    CytologyEvaluation = relationship(
        "CytologyEvaluation", back_populates="Sites"
    )
