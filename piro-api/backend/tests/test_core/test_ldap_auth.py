import pytest
from core.ldap_auth import user_login
from tests.conftest import get_test_db


@pytest.fixture
def patch_bind(monkeypatch):
    """Patch LDAP binding so the login test can run offline."""

    monkeypatch.setattr(
        "core.ldap_auth.try_ldap_bind", lambda *args, **kwargs: True
    )


def test_user_login_fail():
    """Should fail (return False) due to a username with an invalid format."""
    db = next(get_test_db())
    assert not user_login(
        userName="*32#+", password="foobar", islog=True, db=db
    )


def test_user_login_pass(patch_bind):
    """Should succeed."""
    db = next(get_test_db())
    assert user_login(userName="test", password="bar", islog=True, db=db)
