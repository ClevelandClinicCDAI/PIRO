from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Role(Base):
    __tablename__ = "Role"
    RoleId = Column(Integer, primary_key=True, index=True)
    ShortName = Column(String, nullable=False)
    Code = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    DataLabReference = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    UserRole = relationship("UserRole", back_populates="Role")
