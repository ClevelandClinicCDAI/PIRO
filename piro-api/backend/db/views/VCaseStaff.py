from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String


class VCaseStaff(Base):
    __tablename__ = "V_CaseStaffAll"
    CaseStaffId = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, nullable=False)
    StaffId = Column(Integer, nullable=False)
    FullName = Column(String, nullable=False)
    UserId = Column(String, nullable=False)
    StartDate = Column(DateTime(timezone=True))
    EndDate = Column(DateTime(timezone=True), nullable=True)
    CreateDate = Column(DateTime(timezone=True))
    UpdateDate = Column(DateTime(timezone=True), nullable=True)
