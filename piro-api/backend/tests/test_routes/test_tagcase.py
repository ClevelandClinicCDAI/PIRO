from tests.conftest import TestClient


def test_delete_tagcase(client: TestClient, normal_user_token_headers: dict):
    """
    This test requires for the DB to be pre-loaded with data fixtures in the
    `backend.tests.fixtures` directory. If new data is generated using the
    factories within `tests.factories`, then a new `tagcase_id` value will
    need to be defined.
    Args:
        client: TestClient
        normal_user_token_headers: dict

    Returns:

    """
    tagcase_id = 9

    resp = client.delete(
        f"/tagcase/delete/{tagcase_id}", headers=normal_user_token_headers
    )
    assert resp.status_code == 200
    assert resp.json().get("tagcaseid") == tagcase_id
