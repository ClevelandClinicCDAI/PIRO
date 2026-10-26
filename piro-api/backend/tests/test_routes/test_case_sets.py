import json
from urllib.parse import urlencode
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pysolr import Results
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apis.version1.route_case_set import router
from apis.version1.route_teaching_set import router as teaching_router
from core.security_token import create_access_token
from db.base import Base
from db.models.CaseSet import CaseSet, CaseSetCase, CaseSetSpecimen
from db.models.Cohort import Cohort
from db.models.CohortCase import CohortCase
from db.models.Search import Search
from db.models.User import User
from db.repository import case_set
from db.session import get_db, get_solr
from viewmodel.solr.search import SearchDocumentVM


class SearchIndex:
    def __init__(self):
        self.docs = [
            dict(
                id=str(i),
                caseid=i,
                casenumber=f"S26-{i}",
                patientname="Synthetic patient",
                final="Synthetic diagnosis",
                finalcount=1,
                casepatientageyears=40,
            )
            for i in range(1, 7)
        ]
        self.calls = []
        self.fail = False
        self.partial = False

    def search(self, query, **kwargs):
        self.calls.append((query, kwargs))
        if self.fail:
            raise RuntimeError("Synthetic search failure")
        if "cursorMark" in kwargs:
            cursor = kwargs["cursorMark"]
            offset = 0 if cursor == "*" else int(cursor)
            docs = self.docs[offset : offset + kwargs["rows"]]
            return Results(
                {
                    "responseHeader": {"partialResults": self.partial},
                    "response": {"numFound": len(self.docs), "docs": docs},
                    "nextCursorMark": str(offset + len(docs)) if docs else cursor,
                }
            )
        ids = {
            int(i)
            for i in query.removeprefix("caseid:(").removesuffix(")").split(" OR ")
        }
        docs = [d for d in self.docs if d["caseid"] in ids]
        return Results({"response": {"numFound": len(docs), "docs": docs}})


def headers(owner=1, role="USER", attest=False):
    token = create_access_token(
        owner, f"synthetic{owner}", role, "Synthetic", isAttest=attest
    )
    return {"Authorization": "Bearer " + token}


@pytest.fixture
def sets(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    tables = [
        User.__table__,
        Search.__table__,
        Cohort.__table__,
        CohortCase.__table__,
        CaseSet.__table__,
        CaseSetCase.__table__,
        CaseSetSpecimen.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    factory = sessionmaker(bind=engine)
    filters = [
        {
            "field": "final",
            "search": "original",
            "category": "text",
            "andcondition": True,
        }
    ]
    with factory.begin() as db:
        db.execute(
            text(
                "CREATE TABLE Specialty (SpecialtyCategory varchar(100), IsActive bit NOT NULL)"
            )
        )
        db.execute(
            text(
                "INSERT INTO Specialty VALUES ('GI',1),('Derm',1),('GI',1),('Inactive',0),('',1)"
            )
        )
        for owner in (1, 2):
            db.add(
                User(
                    UserId=owner,
                    NUID=str(owner),
                    FirstName="Synthetic",
                    LastName="User",
                    IsActive=True,
                    CreateBy="test",
                )
            )
            db.add(
                Search(
                    SearchId=owner,
                    UserId=owner,
                    Name="Saved search",
                    Description="",
                    SearchQuery="/search?"
                    + urlencode({"searchFilter": json.dumps(filters)}),
                    AdvancedQuery='{"field":"hospital","operator":"=","value":"Test"}',
                    MRN="123",
                    IsActive=True,
                    CreateBy="test",
                )
            )
        db.add(
            Cohort(
                CohortId=1,
                UserId=1,
                Name="Existing cohort",
                Description="",
                Disease="",
                IsFacetDisplay=False,
                IsActive=True,
                LoadType="C",
                IsSolrUpdated=False,
                CreateBy="test",
            )
        )
        for case_id in (1, 1, 3):
            db.add(
                CohortCase(
                    CohortId=1,
                    CaseId=case_id,
                    IsActive=True,
                    LoadType="C",
                    IsSolrUpdated=False,
                    CreateBy="test",
                )
            )
    index = SearchIndex()
    app = FastAPI()
    app.include_router(router, prefix="/case-sets")
    app.include_router(teaching_router, prefix="/teaching-sets")

    def database():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_solr] = lambda: index
    monkeypatch.setattr(case_set, "CAPTURE_BATCH", 2)
    with TestClient(app) as client:
        yield client, factory, index, engine
    engine.dispose()


def create(client, **overrides):
    body = {
        "name": "My fixed set",
        "sourceType": "SAVED_SEARCH",
        "sourceId": 1,
        "operationId": str(uuid4()),
        **overrides,
    }
    response = client.post("/case-sets", json=body, headers=headers())
    assert response.status_code == 201, response.text
    return response.json(), body


def finish(client, item):
    for _ in range(20):
        if item["captureState"] == "READY":
            return item
        response = client.post(
            f'/case-sets/{item["caseSetId"]}/capture',
            json={"cursor": item["captureCursor"]},
            headers=headers(),
        )
        assert response.status_code == 200, response.text
        item = response.json()
        assert item["captureState"] != "FAILED", item
    pytest.fail("Capture did not complete")


def ready_set(db, states, name="A", owner=1):
    item = CaseSet(
        OwnerId=owner,
        Name=name,
        SourceType="COHORT",
        SourceId=1,
        SourceName="Synthetic",
        CreationKey=str(uuid4()),
        CreationHash="test",
        CaptureState="READY",
        CaptureExpected=len(states),
        CaptureSeen=len(states),
    )
    db.add(item)
    db.flush()
    db.add_all(
        [
            CaseSetCase(
                CaseSetId=item.CaseSetId,
                CaseId=case_id,
                Ordinal=ordinal,
                ReviewState=state,
            )
            for ordinal, (case_id, state) in enumerate(states.items(), 1)
        ]
    )
    db.commit()
    return item.CaseSetId


def operation_preview(client, left, right, **changes):
    payload = {
        "leftSetId": left,
        "rightSetId": right,
        "operation": "UNION",
        "membership": "NOT_EXCLUDED",
        **changes,
    }
    response = client.post(
        "/case-sets/operations/preview", json=payload, headers=headers()
    )
    assert response.status_code == 200, response.text
    preview = response.json()
    return preview, {
        **payload,
        "name": "Operation result",
        "operationId": str(uuid4()),
        "leftRevision": preview["left"]["revision"],
        "rightRevision": preview["right"]["revision"],
    }


def cart_payload(**changes):
    return {
        "name": "Selected cases",
        "caseIds": [3, 1, 3],
        "operationId": str(uuid4()),
        **changes,
    }


def test_cart_creates_ready_deduplicated_set_and_retries_without_search(sets):
    client, factory, index, _ = sets
    payload = cart_payload()
    response = client.post("/case-sets/from-cart", json=payload, headers=headers())
    assert response.status_code == 201, response.text
    item = response.json()
    assert item["sourceType"] == "MANUAL" and item["captureState"] == "READY"
    assert item["total"] == item["unreviewed"] == 2
    with factory() as db:
        rows = (
            db.query(CaseSetCase)
            .filter_by(CaseSetId=item["caseSetId"])
            .order_by(CaseSetCase.Ordinal)
            .all()
        )
        assert [r.CaseId for r in rows] == [3, 1]
    index.fail = True
    retry = client.post("/case-sets/from-cart", json=payload, headers=headers())
    assert retry.status_code == 201 and retry.json()["caseSetId"] == item["caseSetId"]
    changed = client.post(
        "/case-sets/from-cart", json={**payload, "caseIds": [2]}, headers=headers()
    )
    assert changed.status_code == 409
    with factory() as db:
        assert db.query(CaseSet).count() == 1


def test_cart_add_is_idempotent_and_preserves_existing_review_specimens_and_position(
    sets,
):
    client, factory, index, _ = sets
    with factory() as db:
        set_id = ready_set(db, {3: "EXCLUDED", 1: "INCLUDED"})
        item = db.get(CaseSet, set_id)
        item.LastCaseId = 1
        item.ReviewFilter = "INCLUDED"
        db.add(
            CaseSetSpecimen(
                CaseSetId=set_id,
                CaseId=1,
                SpecimenId=7,
                SpecimenNumber="Synthetic A",
                SelectedBy=1,
            )
        )
        db.commit()
    path = f"/case-sets/{set_id}/cases"
    response = client.post(path, json={"caseIds": [1, 2, 3, 2, 4]}, headers=headers())
    assert response.status_code == 200, response.text
    item = response.json()
    assert item["added"] == 2 and item["alreadyPresent"] == 2
    assert item["set"]["revision"] == 1
    assert item["set"]["lastCaseId"] == 1 and item["set"]["reviewFilter"] == "INCLUDED"
    with factory() as db:
        rows = (
            db.query(CaseSetCase)
            .filter_by(CaseSetId=set_id)
            .order_by(CaseSetCase.Ordinal)
            .all()
        )
        assert [(r.CaseId, r.ReviewState) for r in rows] == [
            (3, "EXCLUDED"),
            (1, "INCLUDED"),
            (2, "UNREVIEWED"),
            (4, "UNREVIEWED"),
        ]
        assert db.query(CaseSetSpecimen).count() == 1
        assert all(r.Revision == 0 for r in rows)
    index.fail = True
    retry = client.post(path, json={"caseIds": [1, 2, 3, 4]}, headers=headers())
    assert retry.status_code == 200 and retry.json()["added"] == 0
    assert retry.json()["set"]["revision"] == 1


def test_cart_targets_and_add_enforce_owner_active_completed_sets(sets):
    client, factory, _, _ = sets
    with factory() as db:
        own = ready_set(db, {}, "Available")
        other = ready_set(db, {}, "Private", owner=2)
        archived = ready_set(db, {}, "Archived")
        capturing = ready_set(db, {}, "Capturing")
        db.get(CaseSet, archived).Archived = True
        db.get(CaseSet, capturing).CaptureState = "CAPTURING"
        db.commit()
    targets = client.get("/case-sets/cart/targets", headers=headers())
    assert targets.json() == [{"id": own, "name": "Available"}]
    for set_id, status in [(other, 404), (archived, 409), (capturing, 409), (999, 404)]:
        response = client.post(
            f"/case-sets/{set_id}/cases", json={"caseIds": [1]}, headers=headers()
        )
        assert response.status_code == status, response.text
    assert client.post("/case-sets/from-cart", json=cart_payload()).status_code in (
        401,
        403,
    )
    assert client.post(
        f"/case-sets/{own}/cases", json={"caseIds": [1]}
    ).status_code in (401, 403)


@pytest.mark.parametrize(
    "case_ids", [[], [0], [-1], [True], ["1"], list(range(1, 1002))]
)
def test_cart_rejects_invalid_ids_and_oversized_requests(sets, case_ids):
    client, _, _, _ = sets
    response = client.post(
        "/case-sets/from-cart", json=cart_payload(caseIds=case_ids), headers=headers()
    )
    assert response.status_code == 422


@pytest.mark.parametrize("unavailable", [False, True])
def test_cart_validation_failure_does_not_leave_partial_membership(sets, unavailable):
    client, factory, index, _ = sets
    with factory() as db:
        set_id = ready_set(db, {1: "INCLUDED"})
    ids = [2, 3, 999] if unavailable else [2, 3]
    index.fail = not unavailable
    expected = 422 if unavailable else 503
    result = client.post(
        "/case-sets/from-cart", json=cart_payload(caseIds=ids), headers=headers()
    )
    assert result.status_code == expected
    result = client.post(
        f"/case-sets/{set_id}/cases", json={"caseIds": ids}, headers=headers()
    )
    assert result.status_code == expected
    with factory() as db:
        assert db.query(CaseSet).count() == 1
        assert db.query(CaseSetCase).count() == 1
        assert db.get(CaseSet, set_id).Revision == 0


def test_cart_old_schema_has_actionable_error_but_existing_sets_accept_additions(
    sets, monkeypatch
):
    client, factory, _, _ = sets
    with factory() as db:
        set_id = ready_set(db, {})
    real_inspect = case_set.inspect

    class OldSchema:
        def __init__(self, connection):
            self.schema = real_inspect(connection)

        def __getattr__(self, name):
            return getattr(self.schema, name)

        def get_check_constraints(self, name):
            return [
                {
                    "name": "CK_CaseSet_Source",
                    "sqltext": "SourceType IN ('SAVED_SEARCH','COHORT','OPERATION')",
                }
            ]

    monkeypatch.setattr(case_set, "inspect", OldSchema)
    result = client.post("/case-sets/from-cart", json=cart_payload(), headers=headers())
    assert (
        result.status_code == 503
        and "20261021_EnableCaseSetCart.sql" in result.json()["detail"]
    )
    result = client.post(
        f"/case-sets/{set_id}/cases", json={"caseIds": [1]}, headers=headers()
    )
    assert result.status_code == 200


@pytest.mark.parametrize(
    "membership,operation,expected",
    [
        ("NOT_EXCLUDED", "UNION", [1, 2, 3, 4, 5]),
        ("NOT_EXCLUDED", "INTERSECTION", [2]),
        ("NOT_EXCLUDED", "DIFFERENCE", [1, 4]),
        ("NOT_EXCLUDED", "SYMMETRIC_DIFFERENCE", [1, 3, 4, 5]),
        ("INCLUDED_ONLY", "UNION", [2, 3, 4, 5]),
        ("INCLUDED_ONLY", "INTERSECTION", []),
        ("INCLUDED_ONLY", "DIFFERENCE", [2, 4]),
        ("INCLUDED_ONLY", "SYMMETRIC_DIFFERENCE", [2, 3, 4, 5]),
    ],
)
def test_operations_membership_preview_and_independent_result(
    sets, membership, operation, expected
):
    client, factory, index, _ = sets
    left_states = {1: "UNREVIEWED", 2: "INCLUDED", 3: "EXCLUDED", 4: "INCLUDED"}
    right_states = {2: "UNREVIEWED", 3: "INCLUDED", 5: "INCLUDED", 6: "EXCLUDED"}
    with factory() as db:
        left = ready_set(db, left_states)
        right = ready_set(db, right_states, "B")
    preview, payload = operation_preview(
        client, left, right, membership=membership, operation=operation
    )
    assert preview["total"] == len(expected)
    assert preview["left"]["eligible"] == (3 if membership == "NOT_EXCLUDED" else 2)
    response = client.post("/case-sets/operations", json=payload, headers=headers())
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["sourceType"] == "OPERATION" and result["captureState"] == "READY"
    assert result["total"] == result["unreviewed"] == len(expected)
    with factory() as db:
        rows = (
            db.query(CaseSetCase)
            .filter_by(CaseSetId=result["caseSetId"])
            .order_by(CaseSetCase.Ordinal)
            .all()
        )
        assert [r.CaseId for r in rows] == expected
        assert [r.Ordinal for r in rows] == list(range(1, len(expected) + 1))
        assert all(r.ReviewedAt is None and r.ReviewerId is None for r in rows)
        for set_id, original in ((left, left_states), (right, right_states)):
            assert (
                dict(
                    db.query(CaseSetCase.CaseId, CaseSetCase.ReviewState)
                    .filter_by(CaseSetId=set_id)
                    .all()
                )
                == original
            )
            assert db.get(CaseSet, set_id).Revision == 0
        provenance = json.loads(db.get(CaseSet, result["caseSetId"]).SourceQuery)
        assert provenance["left"]["id"] == left and provenance["right"]["id"] == right
        assert (
            provenance["operation"] == operation
            and provenance["membership"] == membership
        )
    assert (
        index.calls == []
    )  # membership uses saved IDs even when cases are unavailable in Solr
    assert result["caseSetId"] in [
        s["id"]
        for s in client.get("/case-sets/operations/sources", headers=headers()).json()
    ]
    chained, _ = operation_preview(client, result["caseSetId"], result["caseSetId"])
    assert chained["total"] == len(expected)


def test_operations_stale_preview_retries_and_direction(sets):
    client, factory, _, _ = sets
    with factory() as db:
        left = ready_set(db, {1: "INCLUDED", 2: "UNREVIEWED"})
        right = ready_set(db, {2: "INCLUDED", 3: "UNREVIEWED"}, "B")
    _, payload = operation_preview(client, left, right, operation="DIFFERENCE")
    assert (
        client.put(
            f"/case-sets/{left}/cases/1",
            json={"state": "EXCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 200
    )
    response = client.post("/case-sets/operations", json=payload, headers=headers())
    assert response.status_code == 409 and "Preview" in response.json()["detail"]
    with factory() as db:
        assert db.query(CaseSet).count() == 2
    preview, payload = operation_preview(client, left, right, operation="DIFFERENCE")
    assert preview["total"] == 0
    reverse, _ = operation_preview(client, right, left, operation="DIFFERENCE")
    assert reverse["total"] == 1
    response = client.post("/case-sets/operations", json=payload, headers=headers())
    assert response.status_code == 201
    result = response.json()
    client.put(
        f"/case-sets/{left}/cases/1",
        json={"state": "INCLUDED", "revision": 1},
        headers=headers(),
    )
    retry = client.post("/case-sets/operations", json=payload, headers=headers())
    assert retry.status_code == 201 and retry.json()["caseSetId"] == result["caseSetId"]
    assert retry.json()["total"] == 0
    assert (
        client.post(
            "/case-sets/operations",
            json={**payload, "name": "Changed"},
            headers=headers(),
        ).status_code
        == 409
    )


@pytest.mark.parametrize(
    "operation,expected",
    [("UNION", 2), ("INTERSECTION", 2), ("DIFFERENCE", 0), ("SYMMETRIC_DIFFERENCE", 0)],
)
def test_operations_identical_operands(sets, operation, expected):
    client, factory, _, _ = sets
    with factory() as db:
        left = ready_set(db, {1: "INCLUDED", 2: "UNREVIEWED"})
    preview, payload = operation_preview(client, left, left, operation=operation)
    assert preview["total"] == expected
    response = client.post("/case-sets/operations", json=payload, headers=headers())
    assert response.status_code == 201 and response.json()["total"] == expected


def test_operation_access_validation_and_source_eligibility(sets):
    client, factory, _, _ = sets
    with factory() as db:
        left = ready_set(db, {})
        foreign = ready_set(db, {}, owner=2)
        archived = ready_set(db, {})
        db.get(CaseSet, archived).Archived = True
        db.commit()
    capturing = create(client)[0]["caseSetId"]
    assert client.get("/case-sets/operations/sources", headers=headers()).json() == [
        {"id": left, "name": "A"}
    ]
    _, payload = operation_preview(client, left, left)
    for route in ("/case-sets/operations/preview", "/case-sets/operations"):
        assert client.post(route, json=payload).status_code == 403
        assert (
            client.post(
                route, json=payload, headers=headers(role="SECURITYADMIN")
            ).status_code
            == 403
        )
        for set_id, status in (
            (foreign, 404),
            (9999, 404),
            (archived, 409),
            (capturing, 409),
        ):
            assert (
                client.post(
                    route, json={**payload, "rightSetId": set_id}, headers=headers()
                ).status_code
                == status
            )
        assert (
            client.post(
                route, json={**payload, "operation": "DROP"}, headers=headers()
            ).status_code
            == 422
        )
    assert (
        client.post(
            "/case-sets/operations", json={**payload, "name": "  "}, headers=headers()
        ).status_code
        == 422
    )


def test_capture_freezes_criteria_collects_all_pages_and_retries_without_duplicates(
    sets,
):
    client, factory, index, _ = sets
    item, payload = create(client)
    assert item["total"] == 0
    assert item["createdAt"].endswith("+00:00")
    with factory.begin() as db:
        source = db.get(Search, 1)
        source.SearchQuery = "/search?" + urlencode({"searchFilter": "[]"})
        source.AdvancedQuery, source.MRN = "{}", "999"
    retry = client.post("/case-sets", json=payload, headers=headers()).json()
    assert retry["caseSetId"] == item["caseSetId"]
    item = finish(client, retry)
    assert item["total"] == item["unreviewed"] == 6
    queries = [q for q, _ in index.calls]
    assert all(
        "original" in q and "Test" in q and "123" in q and "999" not in q
        for q in queries
    )
    assert len({kwargs["NOW"] for _, kwargs in index.calls}) == 1
    assert len(index.calls) == 4
    duplicate = client.post(
        f'/case-sets/{item["caseSetId"]}/capture',
        json={"cursor": "*"},
        headers=headers(),
    ).json()
    assert duplicate["total"] == 6
    with factory() as db:
        assert db.query(CaseSetCase).count() == 6
    another, _ = create(client)
    assert another["caseSetId"] != item["caseSetId"]


def test_review_resume_filters_reversal_conflicts_and_masking(sets):
    client, _, index, _ = sets
    item = finish(client, create(client)[0])
    url = f'/case-sets/{item["caseSetId"]}'
    page = client.get(url + "/cases?size=2", headers=headers()).json()
    assert len(page["items"]) == 2
    assert page["items"][0]["summary"]["patientname"] is None
    assert page["items"][0]["summary"]["finaltexts"] == ["Synthetic diagnosis"]
    admin_page = client.get(url + "/cases", headers=headers(role="ADMIN")).json()
    assert admin_page["items"][0]["summary"]["patientname"] == "Synthetic patient"
    demo_page = client.get(
        url + "/cases", headers=headers(role="DEMOADMIN", attest=True)
    ).json()
    assert demo_page["items"][0]["summary"]["casenumber"] == ""
    assert demo_page["items"][0]["summary"]["patientname"] is None
    decision = {"state": "EXCLUDED", "revision": 0}
    saved = client.put(url + "/cases/1", json=decision, headers=headers())
    assert saved.status_code == 200, saved.text
    assert saved.json()["set"]["excluded"] == 1
    assert saved.json()["set"]["unreviewed"] == 5
    assert (
        client.put(url + "/cases/1", json=decision, headers=headers()).status_code
        == 200
    )
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 409
    )
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "INCLUDED", "revision": 1},
            headers=headers(),
        ).status_code
        == 200
    )
    assert (
        client.get(url + "/cases?filter=EXCLUDED", headers=headers()).json()["total"]
        == 0
    )
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "UNREVIEWED", "revision": 2},
            headers=headers(),
        ).json()["member"]["reviewedAt"]
        is None
    )
    assert (
        client.put(
            url + "/position", json={"caseId": 5, "filter": "ALL"}, headers=headers()
        ).status_code
        == 200
    )
    resumed = client.get(url + "/cases?resume=true&size=2", headers=headers()).json()
    assert resumed["page"] == 3
    assert resumed["items"][0]["caseId"] == 5
    index.docs = [d for d in index.docs if d["caseid"] != 5]
    missing = client.get(url + "/cases?resume=true&size=2", headers=headers()).json()
    assert missing["items"][0]["unavailable"]
    assert missing["set"]["total"] == 6


def test_ownership_authentication_and_membership_validation(sets):
    client, _, _, _ = sets
    item = finish(client, create(client)[0])
    url = f'/case-sets/{item["caseSetId"]}'
    assert client.get("/case-sets").status_code == 403
    assert (
        client.get("/case-sets", headers=headers(role="SECURITYADMIN")).status_code
        == 403
    )
    assert client.get(url, headers=headers(2)).status_code == 404
    assert client.get(url + "/cases", headers=headers(2)).status_code == 404
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(2),
        ).status_code
        == 404
    )
    assert (
        client.put(
            url + "/cases/99",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 404
    )
    assert (
        client.put(
            url + "/position", json={"caseId": 99}, headers=headers()
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/case-sets",
            json={
                "name": "Bad source",
                "sourceType": "SAVED_SEARCH",
                "sourceId": 2,
                "operationId": str(uuid4()),
            },
            headers=headers(),
        ).status_code
        == 404
    )
    assert client.get("/case-sets/sources", headers=headers(2)).json()["cohorts"] == []


def test_capture_failure_resumes_without_loss_and_partial_results_never_become_ready(
    sets,
):
    client, _, index, _ = sets
    item, _ = create(client)
    url = f'/case-sets/{item["caseSetId"]}'
    item = client.post(url + "/capture", json={"cursor": "*"}, headers=headers()).json()
    index.fail = True
    failed = client.post(
        url + "/capture", json={"cursor": item["captureCursor"]}, headers=headers()
    ).json()
    assert failed["captureState"] == "FAILED"
    assert failed["total"] == 2
    assert client.get(url + "/cases", headers=headers()).status_code == 409
    index.fail = False
    assert finish(client, failed)["total"] == 6
    item, _ = create(client)
    index.partial = True
    failed = client.post(
        f'/case-sets/{item["caseSetId"]}/capture',
        json={"cursor": "*"},
        headers=headers(),
    ).json()
    assert failed["captureState"] == "FAILED" and failed["total"] == 0


def test_empty_search_and_duplicate_ids_are_valid(sets):
    client, _, index, _ = sets
    index.docs = []
    assert finish(client, create(client)[0])["total"] == 0
    index.docs = [dict(id=str(i), caseid=1) for i in range(3)]
    item = finish(client, create(client)[0])
    assert item["total"] == 1 and item["captureSeen"] == 3


def test_cohort_capture_is_independent_and_unresolved_members_block_capture(sets):
    client, factory, index, _ = sets
    item, _ = create(client, sourceType="COHORT")
    assert item["captureState"] == "READY" and item["total"] == 2
    assert index.calls == []
    with factory.begin() as db:
        db.query(CohortCase).delete()
        db.add(
            CohortCase(
                CohortId=1,
                CaseId=None,
                IsActive=True,
                LoadType="C",
                IsSolrUpdated=False,
                CreateBy="test",
            )
        )
    assert (
        client.get(f'/case-sets/{item["caseSetId"]}', headers=headers()).json()["total"]
        == 2
    )
    response = client.post(
        "/case-sets",
        json={
            "name": "Unmatched",
            "sourceType": "COHORT",
            "sourceId": 1,
            "operationId": str(uuid4()),
        },
        headers=headers(),
    )
    assert response.status_code == 409
    with factory() as db:
        assert db.query(CaseSet).count() == 1


def test_archive_preserves_membership_and_blocks_review(sets):
    client, _, _, _ = sets
    item = finish(client, create(client)[0])
    url = f'/case-sets/{item["caseSetId"]}'
    result = client.put(
        url,
        json={"name": item["name"], "description": "", "archived": True, "revision": 0},
        headers=headers(),
    )
    assert result.status_code == 200
    assert result.json()["total"] == 6
    assert client.get("/case-sets", headers=headers()).json()["total"] == 0
    assert (
        client.get("/case-sets?archived=true", headers=headers()).json()["total"] == 1
    )
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 409
    )


def test_missing_schema_reports_setup_error(sets):
    client, _, _, engine = sets
    CaseSetCase.__table__.drop(engine)
    response = client.get("/case-sets", headers=headers())
    assert response.status_code == 503
    assert "setup" in response.json()["detail"]


@pytest.mark.parametrize(
    "state,archived",
    [("READY", False), ("READY", True), ("CAPTURING", False), ("FAILED", False)],
)
def test_delete_set_removes_only_its_memberships(sets, state, archived):
    client, factory, index, _ = sets
    with factory() as db:
        target = ready_set(db, {1: "INCLUDED", 2: "EXCLUDED", 3: "UNREVIEWED"})
        other = ready_set(db, {1: "INCLUDED"}, "Keep")
        item = db.get(CaseSet, target)
        item.CaptureState, item.Archived = state, archived
        db.commit()
    response = client.delete(f"/case-sets/{target}?revision=0", headers=headers())
    assert response.status_code == 204 and response.content == b""
    with factory() as db:
        assert db.get(CaseSet, target) is None
        assert db.query(CaseSetCase).filter_by(CaseSetId=target).count() == 0
        assert db.get(CaseSetCase, (other, 1)).ReviewState == "INCLUDED"
        assert db.query(Search).count() == 2
        assert db.query(Cohort).count() == 1
        assert db.query(CohortCase).count() == 3
    assert client.get(f"/case-sets/{target}", headers=headers()).status_code == 404
    assert target not in [
        item["id"]
        for item in client.get(
            "/case-sets/operations/sources", headers=headers()
        ).json()
    ]
    assert (
        client.delete(f"/case-sets/{target}?revision=0", headers=headers()).status_code
        == 404
    )
    assert index.calls == []


def test_delete_preserves_derived_operation_set_and_provenance(sets):
    client, factory, _, _ = sets
    with factory() as db:
        left = ready_set(db, {1: "INCLUDED"}, "Source A")
        right = ready_set(db, {2: "INCLUDED"}, "Source B")
    _, payload = operation_preview(client, left, right)
    result = client.post(
        "/case-sets/operations", json=payload, headers=headers()
    ).json()
    assert (
        client.delete(f"/case-sets/{left}?revision=0", headers=headers()).status_code
        == 204
    )
    with factory() as db:
        derived = db.get(CaseSet, result["caseSetId"])
        assert json.loads(derived.SourceQuery)["left"]["name"] == "Source A"
        assert case_set.counts(derived.CaseSetId, db)["total"] == 2
    assert (
        client.delete(
            f'/case-sets/{result["caseSetId"]}?revision=0', headers=headers()
        ).status_code
        == 204
    )
    with factory() as db:
        assert db.get(CaseSet, right) is not None
        assert db.get(CaseSetCase, (right, 2)) is not None


def test_delete_enforces_owner_role_and_revision(sets):
    client, factory, _, _ = sets
    with factory() as db:
        target = ready_set(db, {1: "UNREVIEWED"})
    url = f"/case-sets/{target}"
    assert client.delete(url + "?revision=0").status_code == 403
    assert (
        client.delete(
            url + "?revision=0", headers=headers(role="SECURITYADMIN")
        ).status_code
        == 403
    )
    assert client.delete(url + "?revision=0", headers=headers(2)).status_code == 404
    assert client.delete(url, headers=headers()).status_code == 422
    assert client.delete(url + "?revision=-1", headers=headers()).status_code == 422
    assert (
        client.put(
            url + "/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 200
    )
    stale = client.delete(url + "?revision=0", headers=headers())
    assert (
        stale.status_code == 409 and "Reload before deleting" in stale.json()["detail"]
    )
    with factory() as db:
        assert db.get(CaseSet, target).Revision == 1
        assert db.get(CaseSetCase, (target, 1)).ReviewState == "INCLUDED"
    assert client.delete(url + "?revision=1", headers=headers()).status_code == 204


REPORT_FIELDS = ("final", "comment", "gross", "synoptic", "intraop", "microscopic")


def test_case_review_includes_full_reports_without_changing_search_previews(sets):
    client, factory, index, _ = sets
    with factory() as db:
        set_id = ready_set(db, {1: "UNREVIEWED"})
    reports = {
        field: f"{field}: " + "Detailed report. " * 120 + f"End {field}"
        for field in REPORT_FIELDS
    }
    index.docs[0].update(reports)
    index.docs[0].update({field + "count": 1 for field in REPORT_FIELDS})
    response = client.get(f"/case-sets/{set_id}/cases?size=1", headers=headers())
    assert response.status_code == 200, response.text
    summary = response.json()["items"][0]["summary"]
    for field in REPORT_FIELDS:
        assert summary[field + "texts"] == [reports[field]]
        assert field not in summary
    preview = SearchDocumentVM(
        age=40,
        interpreter="",
        staffname="",
        final=reports["final"],
        finalcount=1,
        gross=reports["gross"],
        grosscount=1,
    ).dict()
    assert len(preview["finaltexts"][0]) < len(reports["final"])
    assert "End final" not in preview["finaltexts"][0]
    assert "grosstexts" not in preview


def test_case_review_handles_missing_blank_and_rtf_reports(sets):
    client, factory, index, _ = sets
    with factory() as db:
        set_id = ready_set(db, {1: "UNREVIEWED"})
    index.docs[0].update({field: None for field in REPORT_FIELDS})
    index.docs[0].update(final=r"{\rtf1\ansi }", gross=" \n ", microscopic="")
    url = f"/case-sets/{set_id}/cases?size=1"
    response = client.get(url, headers=headers())
    assert response.status_code == 200, response.text
    summary = response.json()["items"][0]["summary"]
    assert all(summary[field + "texts"] == [] for field in REPORT_FIELDS)
    index.docs[0].update(
        gross=r"{\rtf1\ansi Gross\par description}",
        grosscount=1,
        comment="Single diagnostic comment",
        commentcount=2,
        intraop="First   ||||      ||||   Second",
        intraopcount=3,
    )
    summary = client.get(url, headers=headers()).json()["items"][0]["summary"]
    assert summary["grosstexts"] == ["Gross\ndescription"]
    assert summary["commenttexts"] == ["Single diagnostic comment"]
    assert summary["intraoptexts"] == ["First", "Second"]


def test_expanded_case_reports_keep_demo_masking_beyond_preview_limit(sets):
    client, factory, index, _ = sets
    with factory() as db:
        set_id = ready_set(db, {1: "UNREVIEWED"})
    report = "Synthetic report. " * 100 + "S26-123 on 10/15/2026"
    index.docs[0].update({field: report for field in REPORT_FIELDS})
    index.docs[0].update({field + "count": 1 for field in REPORT_FIELDS})
    url = f"/case-sets/{set_id}/cases?size=1"
    summary = client.get(url, headers=headers(role="DEMOADMIN", attest=True)).json()[
        "items"
    ][0]["summary"]
    for field in REPORT_FIELDS:
        value = summary[field + "texts"][0]
        assert "S26-123" not in value and "10/15/2026" not in value
        assert "MM/dd/yyyy" in value
    assert summary["patientname"] is None and summary["casenumber"] == ""
    admin = client.get(url, headers=headers(role="ADMIN")).json()["items"][0]["summary"]
    assert all(admin[field + "texts"] == [report] for field in REPORT_FIELDS)


@pytest.fixture
def specimen_sets(sets):
    client, factory, index, engine = sets
    with engine.begin() as c:
        c.execute(
            text(
                "CREATE TABLE Specimen (SpecimenId INT PRIMARY KEY, CaseId INT, SpecimenNumber VARCHAR(100), IsActive INT)"
            )
        )
        c.execute(
            text(
                "INSERT INTO Specimen VALUES (101,1,'S26-1 A',1),(102,1,'S26-1 B',1),(103,1,'S26-1 Z',1),(104,1,'S26-1 AA',1),(105,1,'S26-1 C',0),(201,3,'S26-3 A',1)"
            )
        )
    with factory() as db:
        set_id = ready_set(db, {1: "UNREVIEWED", 3: "UNREVIEWED"})
    return client, factory, engine, set_id


def test_specimen_selection_persists_and_is_independent_of_decisions_and_other_sets(
    specimen_sets,
):
    client, factory, engine, set_id = specimen_sets
    path = f"/case-sets/{set_id}/cases/1/specimens"
    result = client.get(path, headers=headers()).json()
    assert [s["part"] for s in result["specimens"]] == ["A", "B", "Z", "AA"]
    assert not any(s["selected"] for s in result["specimens"])
    body = {"specimenIds": [101, 104, 104], "revision": 0}
    response = client.put(path, json=body, headers=headers())
    assert response.status_code == 200, response.text
    assert response.json()["member"]["state"] == "UNREVIEWED"
    assert response.json()["member"]["revision"] == 1
    assert (
        client.put(path, json=body, headers=headers()).json()["member"]["revision"] == 1
    )
    result = client.get(path, headers=headers()).json()
    assert [s["specimenId"] for s in result["specimens"] if s["selected"]] == [101, 104]
    with factory() as db:
        other = ready_set(db, {1: "UNREVIEWED"})
        saved = db.get(CaseSetSpecimen, (set_id, 1, 101))
        assert (
            saved.SpecimenNumber == "S26-1 A"
            and saved.SelectedBy == 1
            and saved.SelectedAt
        )
    assert not any(
        s["selected"]
        for s in client.get(
            f"/case-sets/{other}/cases/1/specimens", headers=headers()
        ).json()["specimens"]
    )
    for revision, state in ((1, "EXCLUDED"), (2, "UNREVIEWED")):
        assert (
            client.put(
                f"/case-sets/{set_id}/cases/1",
                json={"state": state, "revision": revision},
                headers=headers(),
            ).status_code
            == 200
        )
    result = client.get(path, headers=headers()).json()
    assert sum(s["selected"] for s in result["specimens"]) == 2
    # Clear all, then select all: neither action marks the case reviewed.
    for revision, ids in ((3, []), (4, [101, 102, 103, 104])):
        response = client.put(
            path, json={"specimenIds": ids, "revision": revision}, headers=headers()
        )
        assert response.status_code == 200, response.text
        assert sum(s["selected"] for s in response.json()["specimens"]) == len(ids)
        assert response.json()["member"]["state"] == "UNREVIEWED"
    # Deleting this set removes its selections, preserving source specimens.
    assert (
        client.delete(f"/case-sets/{set_id}?revision=5", headers=headers()).status_code
        == 204
    )
    with factory() as db:
        assert db.query(CaseSetSpecimen).count() == 0
        assert db.execute(text("SELECT COUNT(*) FROM Specimen")).scalar() == 6
        assert db.get(CaseSet, other) is not None


def test_specimen_selection_validates_ownership_membership_and_revision(specimen_sets):
    client, factory, _, set_id = specimen_sets
    path = f"/case-sets/{set_id}/cases/1/specimens"
    for method in ("get", "put"):
        kwargs = (
            {"json": {"specimenIds": [101], "revision": 0}} if method == "put" else {}
        )
        assert (
            getattr(client, method)(path, headers=headers(2), **kwargs).status_code
            == 404
        )
        assert (
            getattr(client, method)(
                path.replace("/cases/1/", "/cases/999/"), headers=headers(), **kwargs
            ).status_code
            == 404
        )
        assert getattr(client, method)(path, **kwargs).status_code in (401, 403)
    for ids in ([201], [105], [999], [-1], ["101"]):
        assert (
            client.put(
                path, json={"specimenIds": ids, "revision": 0}, headers=headers()
            ).status_code
            == 422
        )
    assert (
        client.put(
            path, json={"specimenIds": [101], "revision": 0}, headers=headers()
        ).status_code
        == 200
    )
    assert (
        client.put(
            path, json={"specimenIds": [102], "revision": 0}, headers=headers()
        ).status_code
        == 409
    )
    assert (
        client.put(
            f"/case-sets/{set_id}/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 409
    )
    with factory.begin() as db:
        db.get(CaseSet, set_id).Archived = True
    assert (
        client.put(
            path, json={"specimenIds": [], "revision": 1}, headers=headers()
        ).status_code
        == 409
    )


def test_unavailable_specimen_selections_are_retained_and_can_be_removed(specimen_sets):
    client, factory, engine, set_id = specimen_sets
    path = f"/case-sets/{set_id}/cases/1/specimens"
    assert (
        client.put(
            path, json={"specimenIds": [101], "revision": 0}, headers=headers()
        ).status_code
        == 200
    )
    with engine.begin() as c:
        c.execute(text("DELETE FROM Specimen WHERE SpecimenId=101"))
    result = client.get(path, headers=headers()).json()
    assert result["specimens"][0] == {
        "specimenId": 101,
        "part": "A",
        "selected": True,
        "available": False,
    }
    response = client.put(
        path, json={"specimenIds": [101, 102], "revision": 1}, headers=headers()
    )
    assert response.status_code == 200
    response = client.put(
        path, json={"specimenIds": [102], "revision": 2}, headers=headers()
    )
    assert response.status_code == 200
    assert 101 not in [s["specimenId"] for s in response.json()["specimens"]]


def test_missing_specimen_migration_does_not_block_case_review(specimen_sets):
    client, _, engine, set_id = specimen_sets
    CaseSetSpecimen.__table__.drop(engine)
    response = client.get(f"/case-sets/{set_id}/cases/1/specimens", headers=headers())
    assert response.status_code == 503
    assert "20261015_AddCaseSetSpecimens.sql" in response.json()["detail"]
    assert (
        client.get(f"/case-sets/{set_id}/cases", headers=headers()).status_code == 200
    )
    assert (
        client.put(
            f"/case-sets/{set_id}/cases/1",
            json={"state": "INCLUDED", "revision": 0},
            headers=headers(),
        ).status_code
        == 200
    )
    assert (
        client.delete(f"/case-sets/{set_id}?revision=1", headers=headers()).status_code
        == 204
    )


def test_specimen_parts_never_expose_accessions_and_empty_cases_are_supported(
    specimen_sets,
):
    client, factory, engine, set_id = specimen_sets
    with engine.begin() as c:
        c.execute(
            text("UPDATE Specimen SET SpecimenNumber='S26-99999' WHERE SpecimenId=101")
        )
    response = client.get(
        f"/case-sets/{set_id}/cases/1/specimens", headers=headers(role="DEMOADMIN")
    )
    assert response.status_code == 200, response.text
    assert "S26-" not in json.dumps(response.json()["specimens"])
    assert "Specimen 101" in json.dumps(response.json()["specimens"])
    with factory() as db:
        empty = ready_set(db, {999: "UNREVIEWED"})
    assert (
        client.get(f"/case-sets/{empty}/cases/999/specimens", headers=headers()).json()[
            "specimens"
        ]
        == []
    )
