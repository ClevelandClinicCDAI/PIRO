from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class SlideRequest(Base):
    __tablename__ = "SlideRequest"
    SlideRequestId = Column(Integer, primary_key=True, index=True)
    AccessionNumber = Column(String, nullable=False)
    CaseType = Column(String, nullable=False)
    Notes = Column(String, nullable=True)
    EPath = Column(Boolean, nullable=False, default=False)
    SlideRoomNotes = Column(String, nullable=True)
    Status = Column(String, nullable=False, default="PENDING")
    UrgencyStatus = Column(String, nullable=False)
    Reason = Column(String, nullable=True)
    DeliveryLocation = Column(String, nullable=True)
    RequesterId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    CompletedById = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    InProcessById = Column(Integer, ForeignKey("User.UserId"), nullable=True)
    # Use timezone-naive datetimes to match the SQL schema (datetime, not datetimeoffset)
    CompletedDate = Column(DateTime(timezone=False), nullable=True)
    CreateDate = Column(DateTime(timezone=False), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=False), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)

    Requester = relationship(
        "User",
        foreign_keys=[RequesterId],
        back_populates="SlideRequests",
    )
    CompletedBy = relationship(
        "User",
        foreign_keys=[CompletedById],
        back_populates="SlideRequestsCompleted",
    )
    InProcessBy = relationship(
        "User",
        foreign_keys=[InProcessById],
        back_populates="SlideRequestsInProcess",
    )
