from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class Staff(Base):
    __tablename__ = "Staff"
    StaffId = Column(Integer, primary_key=True, index=True)
    FullName = Column(String, nullable=False)
    DataLabReference = Column(String, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    CreateDate = Column(DateTime(timezone=True), default=func.now())
    CreateBy = Column(String, nullable=False)
    UpdateDate = Column(DateTime(timezone=True), onupdate=func.now())
    UpdateBy = Column(String, nullable=True)
    # Case = relationship("Case", back_populates="Staff")
