from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class CytologyEvaluation(Base):
    __tablename__ = "CytologyEvaluation"
    CytologyEvaluationId = Column(Integer, primary_key=True, index=True)
    PatientIdentifiers = Column(String, nullable=True)
    ProcedureType = Column(String, nullable=True)
    ProcedurePerformedBy = Column(String, nullable=True)
    EvaluationPerformedBy = Column(String, nullable=True)
    ViaTelecytology = Column(Boolean, nullable=True)
    ReadLocation = Column(String, nullable=True)
    ProcedureLocation = Column(String, nullable=True)
    AssignedToUserId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    ClinicalHistory = Column(String, nullable=True)
    Notes = Column(String, nullable=True)
    PatientHistory = Column(String, nullable=True)
    CytologyPersonnelUserId = Column(
        Integer, ForeignKey("User.UserId"), nullable=True
    )
    PathologistUserId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    FellowUserId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    ResidentUserId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    TotalTimeSpentMinutes = Column(Integer, nullable=True)
    Status = Column(String, nullable=False, default="Draft")
    PrelimVerifierId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    PrelimVerifiedDate = Column(DateTime(timezone=False), nullable=True)
    FinalVerifierId = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    FinalVerifiedDate = Column(DateTime(timezone=False), nullable=True)
    # Use timezone-naive datetimes to match the SQL schema (datetime, not datetimeoffset)
    CreateDate = Column(DateTime(timezone=False), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=False), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)

    AssignedTo = relationship("User", foreign_keys=[AssignedToUserId])
    CytologyPersonnel = relationship(
        "User", foreign_keys=[CytologyPersonnelUserId]
    )
    Pathologist = relationship("User", foreign_keys=[PathologistUserId])
    Fellow = relationship("User", foreign_keys=[FellowUserId])
    Resident = relationship("User", foreign_keys=[ResidentUserId])
    PrelimVerifier = relationship("User", foreign_keys=[PrelimVerifierId])
    FinalVerifier = relationship("User", foreign_keys=[FinalVerifierId])
    Sites = relationship(
        "CytologyEvaluationSite",
        back_populates="CytologyEvaluation",
        order_by="CytologyEvaluationSite.SortOrder",
        cascade="all, delete-orphan",
    )
