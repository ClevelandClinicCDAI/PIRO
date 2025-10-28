import json
import pytest
from tests.conftest import TestClient


@pytest.fixture
def basic_search_adenocarcinoma():
    return {
        "fields": [
            {
                "field": "final;comment;addend",
                "search": "adenocarcinoma",
                "category": "final;comment;addend",
                "andcondition": True,
                "type": "filter",
            }
        ],  # noqa
        "advfields": "{}",
        "mrn": "",
        "url": "/search?searchFilter=%5B%7B%22field%22:%22final;comment;addend%22,%22search%22:%22adenocarcinoma%22,%22category%22:%22final;comment;addend%22,%22andcondition%22:true,%22type%22:%22filter%22%7D%5D&page=1&sortBy=accessiondate",  # noqa
        "page": 1,
        "sortby": "accessiondate",
        "sortorder": "desc",
    }


def test_solr_search(
    client: TestClient,
    normal_user_token_headers: dict,
    basic_search_adenocarcinoma,
):
    response = client.post(
        "/solr/search",
        data=json.dumps(basic_search_adenocarcinoma),
        headers=normal_user_token_headers,
    )

    # mocked solr response won't contain any results, but should have a 200 status code and be properly formatted.
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
