from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String


class VAuditTrail_Report(Base):
    __tablename__ = "V_AuditTrail_Report"
    Date = Column(DateTime(timezone=True), primary_key=True, index=True)
    MonthName = Column(String, nullable=False)
    Month = Column(Integer, nullable=False)
    Year = Column(Integer, nullable=False)
    SearchCount = Column(Integer, nullable=False)
    CaseCount = Column(Integer, nullable=False)
