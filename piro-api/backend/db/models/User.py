from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "User"
    UserId = Column(Integer, primary_key=True, index=True)
    NUID = Column(String, nullable=False)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime, nullable=True, onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    UserRole = relationship("UserRole", back_populates="User")
    Search = relationship("Search", back_populates="User")
    SearchRequest = relationship("SearchRequest", back_populates="User")
    SlideRequests = relationship(
        "SlideRequest",
        back_populates="Requester",
        foreign_keys="SlideRequest.RequesterId",
    )
    SlideRequestsCompleted = relationship(
        "SlideRequest",
        back_populates="CompletedBy",
        foreign_keys="SlideRequest.CompletedById",
    )
    SlideRequestsInProcess = relationship(
        "SlideRequest",
        back_populates="InProcessBy",
        foreign_keys="SlideRequest.InProcessById",
    )
    # AuditTrailSearch = relationship("AuditTrailSearch", back_populates="User")
    # AuditTrailCase = relationship("AuditTrailCase", back_populates="User")
