import json

import pytest
from core.security_token import create_access_token
from db.models.CytologyTerminology import CytologyTerminology
from db.models.User import User
from db.repository.cytology_evaluation import (
    create_cytology_evaluation,
    final_verify_cytology_evaluation,
    prelim_verify_cytology_evaluation,
)
from exception.data_exception import DataException
from tests.conftest import TestClient, get_test_db
from viewmodel.cytology_evaluation import CytologyEvaluationSaveVM

_SEED_TERMINOLOGY = {
    "ProcedureType": ["Bronch", "Superficial/Peripheral FNA", "EUS", "IR"],
    "ReadLocation": ["Main Campus", "Marymount", "Fairview", "Hillcrest"],
    "ProcedureLocation": ["Main Campus", "Marymount", "Fairview", "Hillcrest"],
    "Site": ["Lung, right", "Lung, Left"],
    "Adequacy": ["Non-diagnostic", "Benign"],
}


@pytest.fixture(scope="module", autouse=True)
def seed_cytology_terminology():
    """Populates CytologyTerminology with a minimal subset of the values
    from temp/terminologies.xlsx, mirroring piro-sql/MISC/CytologyTerminology_Seed.sql
    which seeds the real database but is not applied to the ephemeral test DB."""
    db = next(get_test_db())
    for category, values in _SEED_TERMINOLOGY.items():
        for order, value in enumerate(values):
            exists = (
                db.query(CytologyTerminology)
                .filter(CytologyTerminology.Category == category)
                .filter(CytologyTerminology.Value == value)
                .first()
            )
            if not exists:
                db.add(
                    CytologyTerminology(
                        Category=category,
                        Value=value,
                        SortOrder=order,
                        IsActive=True,
                        CreateBy="AutoAdmin",
                    )
                )
    db.commit()


def _base_payload(site_value="Lung, right", adequacy=None):
    return {
        "procedureType": "Bronch",
        "readLocation": "Main Campus",
        "procedureLocation": "Main Campus",
        "viaTelecytology": True,
        "sites": [
            {
                "site": site_value,
                "evalEpisodeNumber": 1,
                "adequacy": adequacy,
                "dqCount": 2,
                "papCount": 1,
                "thinPrepCount": 0,
                "cellBlockCount": 1,
                "unstainedSlidesCount": 3,
            }
        ],
    }


def test_create_evaluation_defaults_to_draft(
    client: TestClient, normal_user_token_headers: dict
):
    """A newly-created evaluation should start in Draft status with totals
    calculated from its site entries."""
    response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Draft"
    assert len(body["sites"]) == 1
    assert body["totals"]["totalDQ"] == 2
    assert body["totals"]["totalPap"] == 1
    assert body["totals"]["totalUnstainedSlides"] == 3


def test_terminology_values_come_from_seeded_list(
    client: TestClient, normal_user_token_headers: dict
):
    response = client.get(
        "/cytologyevaluation/terminology", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "Bronch" in body["procedureType"]
    assert "Main Campus" in body["readLocation"]


def test_invalid_site_value_is_rejected(
    client: TestClient, normal_user_token_headers: dict
):
    """The FastAPI test app used here doesn't register the production
    DataException -> HTTP 510 middleware (see main.py/middleware.py), so
    validation-failure paths are exercised directly against the repository,
    which is what actually raises DataException."""
    db = next(get_test_db())
    payload = CytologyEvaluationSaveVM(**_base_payload(site_value="Not A Real Site"))
    with pytest.raises(DataException):
        create_cytology_evaluation(input=payload, user="test@example.com", db=db)


def test_adding_and_removing_site_entries_updates_totals(
    client: TestClient, normal_user_token_headers: dict
):
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation = create_response.json()
    evaluation_id = evaluation["id"]
    existing_site = evaluation["sites"][0]

    payload = _base_payload()
    payload["sites"] = [
        {**existing_site, "papCount": 5},
        {
            "site": "Lung, Left",
            "evalEpisodeNumber": 2,
            "dqCount": 1,
            "papCount": 1,
            "thinPrepCount": 1,
            "cellBlockCount": 0,
            "unstainedSlidesCount": 0,
        },
    ]
    update_response = client.put(
        f"/cytologyevaluation/{evaluation_id}",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert len(updated["sites"]) == 2
    assert updated["totals"]["totalPap"] == 6
    assert updated["totals"]["totalDQ"] == 3

    # Remove the second site entry entirely; totals should shrink accordingly.
    payload["sites"] = [payload["sites"][0]]
    payload["sites"][0]["id"] = updated["sites"][0]["id"]
    remove_response = client.put(
        f"/cytologyevaluation/{evaluation_id}",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    assert remove_response.status_code == 200
    removed = remove_response.json()
    assert len(removed["sites"]) == 1
    assert removed["totals"]["totalDQ"] == 2


def test_negative_slide_count_is_rejected(
    client: TestClient, normal_user_token_headers: dict
):
    payload = _base_payload()
    payload["sites"][0]["papCount"] = -1
    response = client.post(
        "/cytologyevaluation",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    assert response.status_code == 422


def test_prelim_verify_requires_site_value(
    client: TestClient, normal_user_token_headers: dict
):
    db = next(get_test_db())
    payload = _base_payload()
    payload["sites"][0]["site"] = None
    evaluation = create_cytology_evaluation(
        input=CytologyEvaluationSaveVM(**payload), user="test@example.com", db=db
    )

    with pytest.raises(DataException):
        prelim_verify_cytology_evaluation(
            evaluation_id=evaluation.CytologyEvaluationId,
            user_id=1,
            user="test@example.com",
            db=db,
        )


def test_prelim_then_final_verify_records_verifier_and_timestamp(
    client: TestClient, normal_user_token_headers: dict
):
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]

    prelim_response = client.post(
        f"/cytologyevaluation/{evaluation_id}/prelim-verify",
        headers=normal_user_token_headers,
    )
    assert prelim_response.status_code == 200
    prelim_body = prelim_response.json()
    assert prelim_body["status"] == "Prelim Verified"
    assert prelim_body["prelimVerifierNuid"] is not None
    assert prelim_body["prelimVerifiedDate"] is not None

    # Final verify should fail until every site has an Adequacy value.
    db = next(get_test_db())
    with pytest.raises(DataException):
        final_verify_cytology_evaluation(
            evaluation_id=evaluation_id, user_id=1, user="test@example.com", db=db
        )

    payload = _base_payload(adequacy="Benign")
    payload["sites"][0]["id"] = prelim_body["sites"][0]["id"]
    client.put(
        f"/cytologyevaluation/{evaluation_id}",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )

    final_response = client.post(
        f"/cytologyevaluation/{evaluation_id}/final-verify",
        headers=normal_user_token_headers,
    )
    assert final_response.status_code == 200
    final_body = final_response.json()
    assert final_body["status"] == "Final Verified"
    assert final_body["finalVerifierNuid"] is not None
    assert final_body["finalVerifiedDate"] is not None

    # The form must remain editable after Final Verified for this prototype.
    edit_after_final = client.put(
        f"/cytologyevaluation/{evaluation_id}",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    assert edit_after_final.status_code == 200


def _other_user_token_headers() -> dict:
    """Builds auth headers for a second, unrelated user (not named on any
    evaluation created by the primary test user), to exercise the
    visibility/authorization rules."""
    db = next(get_test_db())
    nuid = "other-user@example.com"
    user = db.query(User).filter(User.NUID == nuid).first()
    if user is None:
        user = User(
            NUID=nuid,
            FirstName="Other",
            LastName="User",
            CreateBy="AutoAdmin",
            IsActive=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(
        userId=user.UserId, nuid=user.NUID, role="USER", name="User, Other"
    )
    return {"Authorization": f"Bearer {token}"}


def test_list_only_returns_evaluations_visible_to_current_user(
    client: TestClient, normal_user_token_headers: dict
):
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]

    own_list = client.get("/cytologyevaluation", headers=normal_user_token_headers)
    assert own_list.status_code == 200
    assert any(item["id"] == evaluation_id for item in own_list.json())

    other_list = client.get(
        "/cytologyevaluation", headers=_other_user_token_headers()
    )
    assert other_list.status_code == 200
    assert all(item["id"] != evaluation_id for item in other_list.json())


def test_unrelated_user_cannot_view_or_edit_evaluation(
    client: TestClient, normal_user_token_headers: dict
):
    """The FastAPI test app used here doesn't register the production
    DataException -> HTTP 510 middleware (see the note on
    test_invalid_site_value_is_rejected above), so an unauthorized-access
    DataException propagates as a raised exception through the test client
    rather than as a non-200 response."""
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]
    other_headers = _other_user_token_headers()

    with pytest.raises(DataException):
        client.get(f"/cytologyevaluation/{evaluation_id}", headers=other_headers)

    with pytest.raises(DataException):
        client.put(
            f"/cytologyevaluation/{evaluation_id}",
            data=json.dumps(_base_payload()),
            headers=other_headers,
        )

    with pytest.raises(DataException):
        client.delete(
            f"/cytologyevaluation/{evaluation_id}", headers=other_headers
        )


def test_named_assignee_can_view_even_if_not_creator(
    client: TestClient, normal_user_token_headers: dict
):
    other_headers = _other_user_token_headers()
    db = next(get_test_db())
    other_user = db.query(User).filter(User.NUID == "other-user@example.com").first()

    payload = _base_payload()
    payload["pathologistUserId"] = other_user.UserId
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]

    get_response = client.get(
        f"/cytologyevaluation/{evaluation_id}", headers=other_headers
    )
    assert get_response.status_code == 200


def test_delete_removes_draft_evaluation(
    client: TestClient, normal_user_token_headers: dict
):
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/cytologyevaluation/{evaluation_id}", headers=normal_user_token_headers
    )
    assert delete_response.status_code == 200

    with pytest.raises(DataException):
        client.get(
            f"/cytologyevaluation/{evaluation_id}", headers=normal_user_token_headers
        )


def test_delete_rejected_once_prelim_verified(
    client: TestClient, normal_user_token_headers: dict
):
    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]
    client.post(
        f"/cytologyevaluation/{evaluation_id}/prelim-verify",
        headers=normal_user_token_headers,
    )

    with pytest.raises(DataException):
        client.delete(
            f"/cytologyevaluation/{evaluation_id}", headers=normal_user_token_headers
        )


def test_completed_endpoint_only_returns_final_verified_evaluations(
    client: TestClient, normal_user_token_headers: dict
):
    draft_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    draft_id = draft_response.json()["id"]

    create_response = client.post(
        "/cytologyevaluation",
        data=json.dumps(_base_payload()),
        headers=normal_user_token_headers,
    )
    evaluation_id = create_response.json()["id"]
    prelim_body = client.post(
        f"/cytologyevaluation/{evaluation_id}/prelim-verify",
        headers=normal_user_token_headers,
    ).json()
    payload = _base_payload(adequacy="Benign")
    payload["sites"][0]["id"] = prelim_body["sites"][0]["id"]
    client.put(
        f"/cytologyevaluation/{evaluation_id}",
        data=json.dumps(payload),
        headers=normal_user_token_headers,
    )
    client.post(
        f"/cytologyevaluation/{evaluation_id}/final-verify",
        headers=normal_user_token_headers,
    )

    completed_response = client.get(
        "/cytologyevaluation/completed", headers=normal_user_token_headers
    )
    assert completed_response.status_code == 200
    completed_ids = [item["id"] for item in completed_response.json()]
    assert evaluation_id in completed_ids
    assert draft_id not in completed_ids
