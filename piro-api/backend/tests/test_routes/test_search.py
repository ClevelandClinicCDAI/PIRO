import json

from tests.conftest import TestClient


def test_create_search(client: TestClient, normal_user_token_headers):
    """
    This function tests a POST request for the `search` endpoint and asserts
    the appropriate response code and returned JSON.
    Args:
        client: Type[TestClient]
        normal_user_token_headers: Annotated[Depends, Type]

    Returns:

    """
    post_data = {
        "name": "Search #1",
        "description": "Maybe think paper true check note hand. Can run " "none teach.",
        "query": "Central understand kitchen theory politics space. Matter "
        "defense leg part resource continue reflect three. Simple four smile "
        "offer.\nFire deal indicate. Republican training admit collection.",
    }

    resp = client.post(
        "/search/create",
        data=json.dumps(post_data),
        headers=normal_user_token_headers,
    )
    assert resp.status_code == 200
    assert resp.json().get("description") == post_data.get("description")
