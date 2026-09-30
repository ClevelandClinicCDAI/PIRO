import json
from unittest import mock

from logger import logger
from tests.conftest import TestClient


def test_create_user(
    client: TestClient,
    normal_user_token_headers,
    mock_create_patch,
):
    mock_patch = "db.repository.user.create_new_user"
    with mock.patch(mock_patch) as mck:
        mck.side_effect = mock_create_patch
        data = {
            "nuid": "testuser@nofoobar.com",
            "firstName": "Homer",
            "lastName": "Simpson",
            "roleId": 2,
            "active": True,
        }
        response = client.post(
            "/user/create",
            data=json.dumps(data),
            headers=normal_user_token_headers,
        )
        logger.info(
            f"Input Data was: {data}\n\nOutput data is:"
            f" {response.json()}\n"
        )
        assert response.status_code == 200
        assert response.json()["nuid"] == "testuser@nofoobar.com"
        assert response.json()["active"] is True
