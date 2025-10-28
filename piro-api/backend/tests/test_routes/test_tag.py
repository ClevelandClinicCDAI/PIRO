import json
from db.models.Tag import Tag
from tests.conftest import TestClient, get_test_db


def test_create_tag(client: TestClient, normal_user_token_headers: dict):
    """Should successfully insert a single tag record."""

    db = next(get_test_db())
    original_tag_count = db.query(Tag.TagId).count()

    post_data = {
        "name": "into",
        "description": "Else well base partner respond player. The shake "
        "civil around much effort skill any.",
    }

    response = client.post(
        "/tag/create",
        data=json.dumps(post_data),
        headers=normal_user_token_headers,
    )

    resulting_tag_count = db.query(Tag.TagId).count()

    assert response.status_code == 200
    assert response.json().get("description") == post_data.get("description")
    assert resulting_tag_count == original_tag_count + 1


def test_all_tags(client: TestClient, normal_user_token_headers: dict):
    """Should successfully return all tags for the test user.

    The test user (ID 50) has at least one active tag in the fixtures that
    should be returned."""

    response = client.get("/tag/all?page=1&size=50", headers=normal_user_token_headers)

    assert response.status_code == 200
    assert response.json()["total"] >= 1  # at least one tag should be returned


def test_tags_dropdown(client: TestClient, normal_user_token_headers: dict):
    """Should return all tags for the test user without pagination.

    The test user (ID 50) has at least one active tag in the fixtures that
    should be returned."""
    response = client.get("tag/dropdown", headers=normal_user_token_headers)

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_tags_get(client: TestClient, normal_user_token_headers: dict):
    """Should return the specified Tag object."""
    response = client.get("tag/get/24", headers=normal_user_token_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "test user tag"


def test_tags_delete(client: TestClient, normal_user_token_headers: dict):
    """Should deactivate a single Tag.

    Note that we don't actually delete records from the database; instead, the
    record will be set 'inactive=True'."""

    db = next(get_test_db())
    original_tag_count = db.query(Tag.TagId).count()

    response = client.delete(
        "/tag/delete/24",
        headers=normal_user_token_headers,
    )

    resulting_tag_count = db.query(Tag.TagId).count()

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert resulting_tag_count == original_tag_count
