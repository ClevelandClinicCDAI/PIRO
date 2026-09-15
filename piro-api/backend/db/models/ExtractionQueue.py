from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ExtractionQueue(Base):
    __tablename__ = "ExtractionQueue"
    __table_args__ = (
        UniqueConstraint(
            "ExtractionSessionId", "CaseId", name="uq_extraction_queue_session_case"
        ),
    )
    ExtractionQueueId = Column(Integer, primary_key=True, index=True)
    ExtractionSessionId = Column(
        Integer, ForeignKey("ExtractionSession.ExtractionSessionId"), nullable=False
    )
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    Status = Column(String(50), nullable=False, default="pending")
    ErrorMessage = Column(String(1000), nullable=True)
    AttemptCount = Column(Integer, nullable=False, default=0)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String(255), nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String(255), nullable=True)

    Session = relationship("ExtractionSession", back_populates="Queue")
    Case = relationship("Case", foreign_keys=[CaseId])

    @property
    def CaseNumber(self) -> str | None:
        return self.Case.CaseNumber if self.Case else None
