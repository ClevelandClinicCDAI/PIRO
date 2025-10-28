import pytest
from core.ldap_auth import user_login
from tests.conftest import get_test_db


@pytest.fixture
def patch_bind(mocker):
    """Apply necessary patching to get the `bind` function running during tests."""
    mocker.patch("core.ldap_auth.try_ldap_bind", return_value=True)


def test_user_login_fail():
    """Should fail (return False) due to a username with an invalid format."""
    db = next(get_test_db())
    assert not user_login(userName="*32#+", password="foobar", islog=True, db=db)


def test_user_login_pass(patch_bind):
    """Should succeed."""
    db = next(get_test_db())
    assert user_login(userName="test", password="bar", islog=True, db=db)
