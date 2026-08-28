from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UnicodeText
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ExtractionRun(Base):
    __tablename__ = "ExtractionRun"
    ExtractionRunId = Column(Integer, primary_key=True, index=True)
    ExtractionSessionId = Column(
        Integer, ForeignKey("ExtractionSession.ExtractionSessionId"), nullable=False
    )
    SchemaJson = Column(UnicodeText, nullable=False)
    LlmProvider = Column(String(100), nullable=False)
    LlmModel = Column(String(255), nullable=False)
    Status = Column(String(50), nullable=False, default="pending")
    RunType = Column(String(50), nullable=False, default="full")
    ValidationSize = Column(Integer, nullable=True)
    CancellationRequested = Column(Boolean, nullable=False, default=False)
    StartedAt = Column(DateTime(timezone=True), nullable=True)
    CompletedAt = Column(DateTime(timezone=True), nullable=True)
    ErrorMessage = Column(UnicodeText, nullable=True)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String(255), nullable=False)

    Session = relationship("ExtractionSession", back_populates="Runs")
    Results = relationship("ExtractionResult", back_populates="Run")
