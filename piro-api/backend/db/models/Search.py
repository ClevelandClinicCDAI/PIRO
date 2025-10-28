from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Search(Base):
    __tablename__ = "Search"
    SearchId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    Name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    SearchQuery = Column(String, nullable=False)
    AdvancedQuery = Column(String, nullable=True)
    MRN = Column(String, nullable=True)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    User = relationship("User", back_populates="Search")
    SearchRequest = relationship("SearchRequest", back_populates="Search")
