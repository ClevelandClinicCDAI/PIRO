from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UnicodeText
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ExtractionSession(Base):
    __tablename__ = "ExtractionSession"
    ExtractionSessionId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    Name = Column(String(255), nullable=False)
    SchemaJson = Column(UnicodeText, nullable=True)
    Status = Column(String(50), nullable=False, default="draft")
    IsActive = Column(Boolean, nullable=False, default=True)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String(255), nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String(255), nullable=True)

    User = relationship("User", foreign_keys=[UserId])
    Queue = relationship("ExtractionQueue", back_populates="Session")
    Runs = relationship("ExtractionRun", back_populates="Session")
