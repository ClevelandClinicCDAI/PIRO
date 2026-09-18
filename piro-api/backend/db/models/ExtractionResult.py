from db.base_class import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    UnicodeText,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ExtractionResult(Base):
    __tablename__ = "ExtractionResult"
    __table_args__ = (
        UniqueConstraint(
            "ExtractionRunId",
            "CaseId",
            "FieldName",
            name="uq_extraction_result_run_case_field",
        ),
    )
    ExtractionResultId = Column(Integer, primary_key=True, index=True)
    ExtractionRunId = Column(
        Integer, ForeignKey("ExtractionRun.ExtractionRunId"), nullable=False
    )
    ExtractionSessionId = Column(
        Integer, ForeignKey("ExtractionSession.ExtractionSessionId"), nullable=False
    )
    CaseId = Column(Integer, ForeignKey("Case.CaseId"), nullable=False)
    FieldName = Column(String(255), nullable=False)
    ExtractedValue = Column(UnicodeText, nullable=True)
    ReviewedValue = Column(UnicodeText, nullable=True)
    Confidence = Column(Float, nullable=True)
    ProvenanceText = Column(UnicodeText, nullable=True)
    SourceCommentId = Column(
        Integer, ForeignKey("CaseComment.CaseCommentId"), nullable=True
    )
    ProvenanceStart = Column(Integer, nullable=True)
    ProvenanceEnd = Column(Integer, nullable=True)
    IsReviewed = Column(Boolean, nullable=False, default=False)
    IsIncorrect = Column(Boolean, nullable=False, default=False)
    ReviewedBy = Column(String(255), nullable=True)
    ReviewedDate = Column(DateTime(timezone=True), nullable=True)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String(255), nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String(255), nullable=True)

    Run = relationship("ExtractionRun", back_populates="Results")
    Case = relationship("Case", foreign_keys=[CaseId])

    @property
    def CaseNumber(self) -> str | None:
        return self.Case.CaseNumber if self.Case else None
