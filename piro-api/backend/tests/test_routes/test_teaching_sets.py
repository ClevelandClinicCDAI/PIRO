import pytest
from sqlalchemy import text

from db.models.CaseSet import CaseSet, CaseSetCase, CaseSetSpecimen
from db.models.User import User
from tests.test_routes import test_case_sets
from tests.test_routes.test_case_sets import headers, ready_set

sets = test_case_sets.sets


def publish(client, sid, category="GI", revision=0, owner=1):
    response = client.put(
        f"/case-sets/{sid}/sharing",
        json={
            "isPublic": True,
            "specialtyCategory": category,
            "revision": revision,
        },
        headers=headers(owner=owner),
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_publication_requires_specialty_preserves_membership_and_handles_retries(sets):
    client, factory, _, _ = sets
    with factory() as db:
        sid = ready_set(db, {1: "INCLUDED", 2: "UNREVIEWED", 3: "EXCLUDED"})
    item = client.get(f"/case-sets/{sid}", headers=headers()).json()
    assert item["isPublic"] is False and item["specialtyCategory"] is None
    assert client.get("/case-sets/specialty-categories", headers=headers()).json() == [
        "Derm",
        "GI",
    ]
    for category in (None, "", " ", "Inactive", "Invented"):
        response = client.put(
            f"/case-sets/{sid}/sharing",
            json={"isPublic": True, "specialtyCategory": category, "revision": 0},
            headers=headers(),
        )
        assert response.status_code == 422, response.text
    item = publish(client, sid, " gi ")
    assert item["specialtyCategory"] == "GI" and item["revision"] == 1
    assert publish(client, sid, revision=0)["revision"] == 1
    conflict = client.put(
        f"/case-sets/{sid}/sharing",
        json={"isPublic": True, "specialtyCategory": "Derm", "revision": 0},
        headers=headers(),
    )
    assert conflict.status_code == 409
    with factory() as db:
        assert db.query(CaseSetCase).count() == 3
        assert db.get(CaseSetCase, (sid, 3)).ReviewState == "EXCLUDED"


def test_catalog_filters_paginates_and_labels_creator_without_private_metadata(sets):
    client, factory, _, _ = sets
    with factory() as db:
        db.get(User, 2).FirstName = "Ada"
        db.get(User, 2).LastName = "Teacher"
        first = ready_set(
            db, {1: "INCLUDED", 2: "UNREVIEWED", 3: "EXCLUDED"}, "A GI teaching"
        )
        second = ready_set(db, {4: "UNREVIEWED"}, "B Derm teaching", owner=2)
        ready_set(db, {5: "UNREVIEWED"}, "Private")
        for name, archived, state in [
            ("Archived", True, "READY"),
            ("Unfinished", False, "CAPTURING"),
        ]:
            sid = ready_set(db, {}, name)
            item = db.get(CaseSet, sid)
            item.IsPublic = True
            item.SpecialtyCategory = "Hidden specialty"
            item.Archived = archived
            item.CaptureState = state
        db.commit()
    publish(client, first)
    publish(client, second, "Derm", owner=2)
    result = client.get("/teaching-sets?size=1", headers=headers(owner=2)).json()
    assert result["total"] == 2 and result["categories"] == ["Derm", "GI"]
    assert result["items"][0]["name"] == "A GI teaching"
    assert result["items"][0]["creatorName"] == "Synthetic User"
    assert result["items"][0]["total"] == 2
    assert (
        client.get("/teaching-sets", headers=headers()).headers["Cache-Control"]
        == "no-store"
    )
    assert set(result["items"][0]) == {
        "caseSetId",
        "name",
        "description",
        "specialtyCategory",
        "creatorName",
        "total",
        "createdAt",
        "updatedAt",
    }
    page2 = client.get("/teaching-sets?size=1&page=2", headers=headers()).json()
    assert page2["items"][0]["creatorName"] == "Ada Teacher"
    filtered = client.get("/teaching-sets?specialty=Derm", headers=headers()).json()
    assert [item["caseSetId"] for item in filtered["items"]] == [second]
    assert filtered["categories"] == ["Derm", "GI"]
    assert (
        client.get("/teaching-sets?specialty=Unknown", headers=headers()).json()[
            "items"
        ]
        == []
    )


def test_view_is_read_only_excludes_rejected_cases_and_uses_viewer_mask(sets):
    client, factory, index, _ = sets
    with factory() as db:
        sid = ready_set(db, {1: "INCLUDED", 2: "EXCLUDED", 3: "UNREVIEWED"})
        item = db.get(CaseSet, sid)
        item.LastCaseId = 2
        item.ReviewFilter = "EXCLUDED"
        db.add(
            CaseSetSpecimen(
                CaseSetId=sid,
                CaseId=1,
                SpecimenId=7,
                SpecimenNumber="S26-1 A",
                SelectedBy=1,
            )
        )
        db.commit()
    publish(client, sid)
    base = f"/teaching-sets/{sid}"
    page = client.get(base + "/cases?size=2", headers=headers(owner=2)).json()
    assert [row["caseId"] for row in page["items"]] == [1, 3]
    assert [row["ordinal"] for row in page["items"]] == [1, 2]
    assert set(page["items"][0]) == {"caseId", "ordinal", "summary", "unavailable"}
    assert page["items"][0]["summary"]["patientname"] is None
    assert (
        client.get(base + "/cases?page=2", headers=headers(owner=2)).json()["items"][0][
            "caseId"
        ]
        == 3
    )
    for role in ("SECURITYADMIN", "SLIDEROOM"):
        response = client.get(base + "/cases", headers=headers(owner=2, role=role))
        assert response.status_code == 200, response.text
        assert response.json()["items"][0]["summary"]["patientname"] is None
    admin = client.get(base + "/cases", headers=headers(owner=2, role="ADMIN")).json()
    assert admin["items"][0]["summary"]["patientname"] == "Synthetic patient"
    demo = client.get(
        base + "/cases", headers=headers(owner=2, role="DEMOADMIN", attest=True)
    ).json()
    assert demo["items"][0]["summary"]["casenumber"] == ""
    with factory() as db:
        item = db.get(CaseSet, sid)
        assert (item.LastCaseId, item.ReviewFilter, item.Revision) == (2, "EXCLUDED", 1)
        assert db.query(CaseSetSpecimen).count() == 1
    index.docs = [doc for doc in index.docs if doc["caseid"] != 1]
    assert (
        client.get(base + "/cases", headers=headers(owner=2)).json()["items"][0][
            "unavailable"
        ]
        is True
    )


def test_access_requires_active_login_and_never_grants_owner_operations(sets):
    client, factory, _, _ = sets
    with factory() as db:
        sid = ready_set(db, {1: "INCLUDED"})
        private = ready_set(db, {2: "INCLUDED"})
    publish(client, sid)
    for path in (
        "/teaching-sets",
        f"/teaching-sets/{sid}",
        f"/teaching-sets/{sid}/cases",
    ):
        assert client.get(path).status_code in (401, 403)
        assert client.get(path, headers=headers(owner=999)).status_code == 403
    for path in (
        f"/teaching-sets/{private}",
        f"/teaching-sets/{private}/cases",
        "/teaching-sets/999",
    ):
        assert client.get(path, headers=headers(owner=2)).status_code == 404
    base = f"/case-sets/{sid}"
    for method, suffix, body in [
        ("get", "", None),
        ("get", "/cases", None),
        ("get", "/cases/1/specimens", None),
        ("put", "/sharing", {"isPublic": False, "revision": 1}),
        ("put", "/cases/1", {"state": "EXCLUDED", "revision": 0}),
        ("put", "/position", {"caseId": 1, "filter": "ALL"}),
        ("post", "/cases", {"caseIds": [2]}),
    ]:
        response = client.request(
            method, base + suffix, json=body, headers=headers(owner=2)
        )
        assert response.status_code == 404, response.text
    assert (
        client.get("/case-sets/operations/sources", headers=headers(owner=2)).json()
        == []
    )
    with factory.begin() as db:
        db.get(User, 2).IsActive = False
    assert client.get("/teaching-sets", headers=headers(owner=2)).status_code == 403


def test_unpublish_archive_and_delete_remove_discovery_and_direct_access(sets):
    client, factory, _, _ = sets
    with factory() as db:
        sid = ready_set(db, {1: "UNREVIEWED"})
    published = publish(client, sid)
    with factory.begin() as db:
        db.execute(text("UPDATE Specialty SET IsActive=0 WHERE SpecialtyCategory='GI'"))
    response = client.put(
        f"/case-sets/{sid}/sharing",
        json={"isPublic": False, "revision": published["revision"]},
        headers=headers(),
    )
    assert response.status_code == 200
    assert client.get("/teaching-sets", headers=headers(owner=2)).json()["total"] == 0
    assert (
        client.get(f"/teaching-sets/{sid}/cases", headers=headers(owner=2)).status_code
        == 404
    )
    publish(client, sid, "Derm", revision=response.json()["revision"])
    with factory.begin() as db:
        db.get(CaseSet, sid).Archived = True
    assert (
        client.get(f"/teaching-sets/{sid}", headers=headers(owner=2)).status_code == 404
    )
    assert client.get("/teaching-sets", headers=headers(owner=2)).json()["total"] == 0
    with factory.begin() as db:
        db.get(CaseSet, sid).Archived = False
    current = client.get(f"/case-sets/{sid}", headers=headers()).json()
    assert (
        client.delete(
            f"/case-sets/{sid}?revision={current['revision']}", headers=headers()
        ).status_code
        == 204
    )
    assert (
        client.get(f"/teaching-sets/{sid}", headers=headers(owner=2)).status_code == 404
    )


@pytest.mark.parametrize(
    "archived,state", [(True, "READY"), (False, "CAPTURING"), (False, "FAILED")]
)
def test_cannot_publish_archived_or_incomplete_sets(sets, archived, state):
    client, factory, _, _ = sets
    with factory() as db:
        sid = ready_set(db, {})
        item = db.get(CaseSet, sid)
        item.Archived = archived
        item.CaptureState = state
        db.commit()
    response = client.put(
        f"/case-sets/{sid}/sharing",
        json={"isPublic": True, "specialtyCategory": "GI", "revision": 0},
        headers=headers(),
    )
    assert response.status_code == 409
