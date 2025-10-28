from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TagCase(Base):
    __tablename__ = "TagCase"
    TagCaseId = Column(Integer, primary_key=True, index=True)
    TagId = Column(Integer, ForeignKey("Tag.TagId"), nullable=False)
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    Tag = relationship("Tag", back_populates="TagCase")
    Case = relationship("Case", back_populates="TagCase")
