import pytest
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from logger import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database
from pysolr import Results
from apis.base import api_router
from core.auth_bearer import JWTBearer
from core.config import settings
from core.constants import Constants
from core.security_token import create_access_token
from crud.crud import write_row
from db.models.Role import Role
from db.models.User import User
from db.models.UserRole import UserRole
from db.views.VCase import VCase
from tests.consts import SQLA_DB_URL
from db.base_class import Base  # noqa E402
from db.session import get_db, get_solr  # noqa E402


# ############################## #
# ##### Solr Configuration ##### #
class MockSolrResults(Results):
    """Mock object mimicking a 'Results' object from the pysolr library."""


class MockSolr:
    """Mock object to replicate data returned by Solr in unit tests.

    Used in place of an actual Solr instance to simplify testing."""

    def search(self, q, search_handler=None, **kwargs):
        return MockSolrResults(decoded={})


def get_mock_solr():
    """Return the mock Solr client used during tests."""
    return MockSolr()


# ################################## #
# ##### Database Configuration ##### #
def get_test_db() -> Generator:
    """Returns a session generator ('db') for the test database.

    To access the session, call 'next(get_test_db())'."""
    engine = create_engine(
        SQLA_DB_URL, connect_args={"check_same_thread": False}
    )
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Create a fresh SQLite test database for the session."""

    sqlite_path = Path(SQLA_DB_URL.replace("sqlite:///", ""))
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    # recreate the database
    if database_exists(SQLA_DB_URL):
        drop_database(SQLA_DB_URL)
    create_database(SQLA_DB_URL)

    # create the application tables only; individual tests now create the
    # records they need explicitly.
    engine = create_engine(
        SQLA_DB_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)


# ############################################### #
# ##### User & Authentication Configuration ##### #
def get_test_user(db: Session) -> User:
    """Get or create a user to use for testing."""
    email = settings.TEST_USER_EMAIL

    user = db.query(User).filter(User.NUID == email).first()

    if user:
        return user

    # otherwise, create a new one
    user_data = {
        "NUID": email,
        "FirstName": "David",
        "LastName": "Dixon",
        "CreateBy": "AutoAdmin",
        "IsActive": True,
    }
    _, user = write_row(data_row=User(**user_data), session_inst=db)

    return user


def get_and_configure_test_role(db: Session, user: User) -> Role:
    """Create a user-role link for the test user and return the role."""

    role = db.query(Role).filter(Role.Code == "csmt").first()
    if not role:
        role_data = {
            "RoleId": 2,
            "ShortName": Constants.RoleAdmin,
            "Code": "csmt",
            "Description": "Test role",
            "DataLabReference": "Test reference",
            "IsActive": True,
            "CreateBy": "AutoAdmin",
        }
        _, role = write_row(data_row=Role(**role_data), session_inst=db)

    user_role = (
        db.query(UserRole).filter(UserRole.UserId == user.UserId).first()
    )
    if not user_role:
        user_role_data = {
            "IsActive": True,
            "UserId": user.UserId,
            "RoleId": role.RoleId,
            "CreateBy": "AutoAdmin",
        }
        write_row(data_row=UserRole(**user_role_data), session_inst=db)

    return role


def get_mock_jwt_bearer_token() -> None:
    """Generates a JWT bearer token suitable for use in tests."""

    return None


@pytest.fixture
def normal_user_token_headers():
    """Returns a header with a JWT bearer token suitable for use in tests.

    The token is tied to the test user created in this module.
    """

    db = next(get_test_db())
    user = get_test_user(db)
    role = get_and_configure_test_role(db, user)

    mock_jwt_bearer_token = create_access_token(
        userId=user.UserId,
        nuid=user.NUID,
        role=role.ShortName,
        name=f"{user.LastName}, {user.FirstName}",
    )
    return {"Authorization": f"Bearer {mock_jwt_bearer_token}"}


# ############################################### #
# ##### Test App and Client Configuration ##### #
def get_test_app():
    """Instantiate the FastAPI test app with dependency overrides."""
    app = FastAPI()
    app.include_router(api_router)
    add_pagination(app)
    app.dependency_overrides[
        JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin])
    ] = get_mock_jwt_bearer_token
    app.dependency_overrides[get_solr] = get_mock_solr
    app.dependency_overrides[get_db] = get_test_db
    return app


@pytest.fixture(scope="module")
def client():
    """Key fixture that defines the TestClient for use in our unit tests."""
    app = get_test_app()
    with TestClient(app) as client:
        yield client


# ############################ #
# ##### General Fixtures ##### #
@pytest.fixture(name="mock_create_patch", scope="session")
def patch_create_user() -> Callable:
    """
    Created as a mock patch to bypass `db.repository.user.create_new_user`.
    May not be needed now that SQLite PK ID field autoincrement issue is
    resolved.
    Returns:

    """

    def new_create_user(user, current_user, db):
        new_user_dict = {
            "NUID": user.nuid,
            "FirstName": user.firstName,
            "LastName": user.lastName,
            "IsActive": True,
            "CreateBy": current_user,
        }

        new_user = User(**new_user_dict)
        success, row = write_row(new_user, db)
        if success:
            logger.info(
                f"Data successfully written to db! See the payload: "
                f"{new_user_dict}"
            )
            role_data = {
                "RoleId": user.roleId,
                "UserId": row.UserId,
                "IsActive": True,
                "CreateBy": current_user,
            }
            new_user_role = UserRole(**role_data)
            _, user_role = write_row(new_user_role, db)
        else:
            logger.debug(
                f"Data failed to write to the DB. Success "
                f"status is {success} and the data object instance has a "
                f"object value of {row}. We'll just return "
                f"the User instance to facilitate testing. We'll "
                f"debug the DB issue at a later time."
            )

            new_user = User(**new_user_dict)
            logger.info(new_user_dict)
        return new_user

    return new_create_user


@pytest.fixture
def vcase_one():
    """Basic VCase object for use in tests."""
    return VCase(
        AccessionDate=datetime.now(),
        ReceiveDate=datetime.now(),
        OverdueDate=datetime.now(),
        CollectionDate=datetime.now(),
        SignoutDate=datetime.now(),
        PatientName="Testy McTesterson",
        PatientDOB=datetime.now(),
        PatientEpi="E11111111",
        PatientMrn="11111111",
        PatientLanguage="English",
        PatientEthnicity=None,
        PatientDeathDate=None,
        PatientIsDeceased=False,
        PatientRace=None,
        PatientCity=None,
        PatientState=None,
        PatientCountry=None,
    )
