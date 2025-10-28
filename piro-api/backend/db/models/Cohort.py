from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class Cohort(Base):
    __tablename__ = "Cohort"
    CohortId = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    Disease = Column(String, nullable=False)
    UserId = Column(Integer, nullable=False)
    IsFacetDisplay = Column(Boolean, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    LoadType = Column(String, nullable=False)
    IsSolrUpdated = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
