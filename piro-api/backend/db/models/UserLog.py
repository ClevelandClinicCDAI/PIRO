from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class UserLog(Base):
    __tablename__ = "UserLog"
    UserLogId = Column(Integer, primary_key=True, index=True)
    NUID = Column(String, nullable=True)
    UserId = Column(Integer, nullable=True)
    RoleId = Column(Integer, nullable=True)
    Code = Column(String, nullable=True)
    Type = Column(String, nullable=True)
    Message = Column(String, nullable=True)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
