from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Tag(Base):
    __tablename__ = "Tag"
    TagId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    Name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    TagCase = relationship("TagCase", back_populates="Tag")
