from db.base_class import Base
from sqlalchemy import Column, Integer, String


class VCaseMrn(Base):
    __tablename__ = "V_Case_MRN"
    CaseId = Column(Integer, primary_key=True, index=True)
    CaseNumber = Column(String, nullable=False)
    PatientMrn = Column(String, nullable=False)
