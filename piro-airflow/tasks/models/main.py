from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mssql import VARCHAR

Base = declarative_base()


class CaseTextMasterPlain(Base):
    __tablename__ = "CaseTextMasterPlain"

    PlainTextId = Column(Integer, primary_key=True, autoincrement=True)
    CaseId = Column(Integer)
    CaseNumber = Column(String(100))
    CommentTypeId = Column(Integer)
    RefLabCompName = Column(String(100))
    CaseCommentCoEpicId = Column(Integer, nullable=True)
    CaseCommentCoPathId = Column(Integer, nullable=True)
    CaseCommentId = Column(Integer, nullable=True)
    plain_Text = Column(VARCHAR(None))  # VARCHAR(None) == Varchar(max) for SQL Server      # noqa: E501
