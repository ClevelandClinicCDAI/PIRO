from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.sql import func


class CaseCommentSynopticSpecimen(Base):
    __tablename__ = "CaseCommentSynopticSpecimen"
    Id = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, nullable=False)
    SpecimenId = Column(Integer, nullable=False)
    SynopticId = Column(Integer, nullable=False)
    SynopticLine = Column(Integer, nullable=False)
    CaseNum = Column(String, nullable=False)
    SpecimenNum = Column(String, nullable=False)
    SpecimenList = Column(String, nullable=True)
    RecordCreateDate = Column(DateTime, nullable=True)
    IsSpecimenLevel = Column(Boolean, nullable=True)
    RefSpecimenKey = Column(String, nullable=False)
    RefRequisitionKey = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
