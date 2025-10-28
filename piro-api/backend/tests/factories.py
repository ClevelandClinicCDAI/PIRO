import random
from datetime import date, datetime, timedelta

import factory
from db.models.Role import Role
from db.models.Search import Search
from db.models.SearchRequest import SearchRequest
from db.models.SearchRequestStatus import SearchRequestStatus
from db.models.Tag import Tag
from db.models.TagCase import TagCase
from db.models.User import User as PiroUser
from db.models.UserRole import UserRole
from polyfactory.factories.pydantic_factory import ModelFactory
from tests.db import session_inst
from viewmodel.solr.search import (
    SearchDocumentVM,
    SearchFilterVM,
    SearchInputVM,
)

# session_inst = scoped_session(
#     sessionmaker(autocommit=False, autoflush=False, bind=engine)
# )


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    IsActive = factory.Faker("pybool")
    CreateDate = factory.Faker("date_time")
    CreateBy = factory.Faker("name")
    UpdateDate = factory.LazyAttribute(
        lambda o: get_random_later_date(o.CreateDate)
    )
    UpdateBy = factory.LazyAttribute(lambda o: o.CreateBy)


class SearchFactory(BaseFactory):
    class Meta:
        model = Search
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    SearchId = factory.Sequence(lambda n: n + 1)
    Name = factory.Faker("text", max_nb_chars=100)
    Description = factory.Faker("text", max_nb_chars=150)
    SearchQuery = factory.Faker("text", max_nb_chars=200)
    SearchRequest = factory.RelatedFactory(
        "tests.factories.SearchRequestFactory", factory_related_name="Search"
    )

    @factory.iterator
    def User():  # noqa
        yield from session_inst().query(PiroUser).all()


class SearchRequestStatusFactory(BaseFactory):
    class Meta:
        model = SearchRequestStatus
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    SearchRequestStatusId = factory.Sequence(lambda n: n)
    ShortName = factory.Faker("text", max_nb_chars=100)
    Code = factory.Faker("pystr")
    Description = factory.Faker("text", max_nb_chars=250)
    # SearchRequest = factory.SubFactory(SearchRequestFactory)


class SearchRequestFactory(BaseFactory):
    class Meta:
        model = SearchRequest
        sqlalchemy_session = session_inst

    SearchRequestId = factory.Sequence(lambda n: n + 1)
    # RequesterId = factory.LazyAttribute(lambda o: o.Search.User.UserId)
    RequestName = factory.Faker("word")
    # RequestDocumentFile = factory.Faker()
    # RequestDocumentName = factory.Faker()
    # RequestDocumentSize = factory.Faker()
    RequestComment = factory.Faker("text", max_nb_chars=150)
    SearchRequestReasonId = factory.LazyAttribute(
        lambda o: random.randint(0, 3000)
    )
    ApprovedById = factory.Faker("name")
    ApprovedDate = factory.Faker("date_time")
    ApprovalComment = factory.Iterator(
        [
            "Approved!",
            "Just confirm with George Wendt",
            "Didn't read the request but I trust you!",
        ]
    )
    # User = factory.Iterator(session_inst.query(PiroUser).all())
    # Search = factory.Iterator(searches)
    SearchRequestStatus = factory.SubFactory(SearchRequestStatusFactory)

    @factory.iterator
    def Search():  # noqa
        yield from session_inst().query(Search).all()

    @factory.iterator
    def User():  # noqa
        yield from session_inst().query(PiroUser).all()

    @factory.post_generation
    def default_package(self, create, _, **__):
        SearchRequestStatusFactory(SearchRequest=[self])


class UserFactory(BaseFactory):
    class Meta:
        model = PiroUser
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    UserId = factory.Sequence(lambda n: n)
    NUID = factory.LazyAttribute(
        lambda o: f"{o.FirstName.lower()}."
        f"{o.LastName.lower()}@fakedomain.org"
    )
    FirstName = factory.Faker("first_name")
    LastName = factory.Faker("last_name")
    UserRole = factory.RelatedFactory(
        "tests.factories.UserRoleFactory",
        factory_related_name="User",
    )


class RoleFactory(BaseFactory):
    class Meta:
        model = Role
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    RoleId = factory.Sequence(lambda n: n)
    ShortName = factory.Iterator(["USER", "ADMIN", "ANALYST"])
    Code = factory.Faker("pystr", max_chars=4)
    Description = factory.Faker("text", max_nb_chars=200)
    DataLabReference = factory.LazyAttribute(lambda o: o.Code.upper())


class UserRoleFactory(BaseFactory):
    class Meta:
        model = UserRole
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    UserRoleId = factory.Sequence(lambda n: n)
    Role = factory.SubFactory(RoleFactory)

    @factory.post_generation
    def default_package(self, create, _, **__):
        UserFactory(UserRole=self)
        # RoleFactory()


class TagFactory(BaseFactory):
    class Meta:
        model = Tag
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    TagId = factory.Sequence(lambda n: n)
    Name = factory.Faker("word")
    Description = factory.Faker("text", max_nb_chars=200)
    TagCase = factory.RelatedFactory(
        "tests.factories.TagCaseFactory", factory_related_name="Tag"
    )

    @factory.iterator
    def UserId():  # noqa
        yield from list(
            map(
                lambda x: x.UserId, session_inst().query(PiroUser.UserId).all()
            )
        )

    # TagCase = factory.SubFactory("tests.factories.TagCaseFactory")


class TagCaseFactory(BaseFactory):
    class Meta:
        model = TagCase
        sqlalchemy_session = session_inst
        # sqlalchemy_session_factory_persistence = "commit"

    TagCaseId = factory.Sequence(lambda n: n)

    CaseId = factory.Faker("pyint", max_value=200)


SearchFilterVMFactory, SearchInputVMFactory, SearchDocumentVMFactory = list(
    map(
        ModelFactory.create_factory,
        [SearchFilterVM, SearchInputVM, SearchDocumentVM],
    )
)


def get_random_later_date(date_obj: date | datetime):
    """
    A small utility function to produce a randomly generated date that is
    later from the fed date_obj arg. Intended for producing Updated date
    field values in testing units.
    Args:
        date_obj: date | datetime

    Returns: date

    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()

    today = date.today()
    date_range = today - date_obj

    new_date = today - timedelta(random.randint(1, date_range.days))

    return new_date
