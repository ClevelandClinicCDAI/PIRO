import json

from db.models.Tag import Tag
from tests.conftest import TestClient, get_test_db, get_test_user


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

    The test creates its own tag and then checks that the response includes
    at least that row.
    """

    db = next(get_test_db())
    user = get_test_user(db)
    tag = Tag(
        UserId=user.UserId,
        Name="all-tags-case",
        Description="Tag created for the all-tags test.",
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tag)
    db.commit()

    response = client.get(
        "/tag/all?page=1&size=50", headers=normal_user_token_headers
    )

    assert response.status_code == 200
    assert response.json()["total"] >= 1  # at least one tag should be returned


def test_tags_dropdown(client: TestClient, normal_user_token_headers: dict):
    """Should return all tags for the test user without pagination.

    The test creates its own tag and then checks that the dropdown has at
    least one entry.
    """
    db = next(get_test_db())
    user = get_test_user(db)
    tag = Tag(
        UserId=user.UserId,
        Name="dropdown-case",
        Description="Tag created for the dropdown test.",
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tag)
    db.commit()

    response = client.get("tag/dropdown", headers=normal_user_token_headers)

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_tags_get(client: TestClient, normal_user_token_headers: dict):
    """Should return the specified Tag object."""

    db = next(get_test_db())
    user = get_test_user(db)
    tag = Tag(
        UserId=user.UserId,
        Name="lookup-tag",
        Description="Tag created for the get test.",
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    response = client.get(
        f"tag/get/{tag.TagId}", headers=normal_user_token_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == tag.Name


def test_tags_delete(client: TestClient, normal_user_token_headers: dict):
    """Should deactivate a single Tag.

    Note that we don't actually delete records from the database; instead, the
    record will be set 'inactive=True'."""

    db = next(get_test_db())
    user = get_test_user(db)
    tag = Tag(
        UserId=user.UserId,
        Name="delete-tag",
        Description="Tag created for the delete test.",
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    response = client.delete(
        f"/tag/delete/{tag.TagId}",
        headers=normal_user_token_headers,
    )

    db.expire_all()
    updated_tag = db.query(Tag).filter(Tag.TagId == tag.TagId).first()

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert updated_tag is not None
    assert updated_tag.IsActive is False
