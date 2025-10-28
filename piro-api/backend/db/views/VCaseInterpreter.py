from db.base_class import Base
from sqlalchemy import Column, DateTime, Integer, String


class VCaseInterpreter(Base):
    __tablename__ = "V_InterpreterAll"
    InterpreterId = Column(Integer, primary_key=True, index=True)
    CaseId = Column(Integer, nullable=False)
    Interpreter = Column(String, nullable=False)
    ProcedureCategory = Column(String, nullable=False)
    CreateDate = Column(DateTime(timezone=True))
    UpdateDate = Column(DateTime(timezone=True), nullable=True)
