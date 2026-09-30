from db.models.Tag import Tag
from db.models.TagCase import TagCase
from tests.conftest import TestClient, get_test_db, get_test_user


def test_delete_tagcase(client: TestClient, normal_user_token_headers: dict):
    """
    The test now creates the exact tag/tagcase rows it needs instead of
    depending on pre-loaded fixtures.
    Args:
        client: TestClient
        normal_user_token_headers: dict

    Returns:

    """
    db = next(get_test_db())
    user = get_test_user(db)
    tag = Tag(
        UserId=user.UserId,
        Name="tagcase-tag",
        Description="Tag created for the tagcase test.",
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    tagcase = TagCase(
        TagId=tag.TagId,
        CaseId=1,
        IsActive=True,
        CreateBy=user.NUID,
    )
    db.add(tagcase)
    db.commit()
    db.refresh(tagcase)

    resp = client.delete(
        f"/tagcase/delete/{tagcase.TagCaseId}",
        headers=normal_user_token_headers,
    )
    assert resp.status_code == 200
    assert resp.json().get("tagcaseid") == tagcase.TagCaseId
