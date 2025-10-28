from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class UserRole(Base):
    __tablename__ = "UserRole"
    UserRoleId = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    RoleId = Column(Integer, ForeignKey("Role.RoleId"), nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    User = relationship("User", back_populates="UserRole")
    Role = relationship("Role", back_populates="UserRole")
