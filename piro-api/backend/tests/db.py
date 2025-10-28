from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tests.consts import SQLA_DB_URL

engine = create_engine(SQLA_DB_URL, connect_args={"check_same_thread": False})
made_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session_inst = scoped_session(made_session)
