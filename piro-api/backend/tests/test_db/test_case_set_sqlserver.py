"""Run only against an explicitly configured disposable SQL Server instance."""

import os
import re
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Barrier
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from db.base import Base  # noqa: F401 -- register the application's related models
from db.models.Cohort import Cohort
from db.models.CohortCase import CohortCase
from db.models.CaseSet import CaseSet, CaseSetCase, CaseSetSpecimen
from db.repository import case_set
from tests.test_routes.test_case_sets import SearchIndex, ready_set
from viewmodel.case_set import (
    CaseSetCreate,
    CaseSetDecision,
    CaseSetOperationCreate,
    CaseSetOperationPreview,
    CaseSetSpecimenSelection,
    CaseSetAddCases,
    CaseSetCartCreate,
)

SQL_ROOT = Path(__file__).resolve().parents[4] / "piro-sql"


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    # Override the shared SQLite fixture; these tests own isolated SQL Server DBs.
    pass


@pytest.fixture
def sql_database():
    url = os.environ.get("PIRO_CASE_SET_TEST_URL")
    if not url:
        pytest.skip(
            "Set PIRO_CASE_SET_TEST_URL to a disposable SQL Server master database."
        )
    master = create_engine(url, isolation_level="AUTOCOMMIT")
    database = "piro_case_set_test_" + uuid4().hex
    with master.connect() as c:
        c.exec_driver_sql(f"CREATE DATABASE [{database}]")
    engine = create_engine(master.url.set(database=database))
    try:
        with engine.begin() as c:
            c.exec_driver_sql(
                "CREATE TABLE dbo.[User](UserId int PRIMARY KEY); INSERT dbo.[User] VALUES(1)"
            )
            for name in ("Cohort", "CohortCase"):
                data = (SQL_ROOT / "Table" / f"dbo.{name}.Table.sql").read_bytes()
                script = data.decode(
                    "utf-16"
                    if data.startswith((b"\xff\xfe", b"\xfe\xff"))
                    else "utf-8-sig"
                )
                for batch in re.split(r"^GO\s*$", script, flags=re.M | re.I):
                    if batch.strip():
                        c.exec_driver_sql(batch)
        yield engine, database
    finally:
        engine.dispose()
        with master.connect() as c:
            c.exec_driver_sql(
                f"ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"
            )
            c.exec_driver_sql(f"DROP DATABASE [{database}]")
        master.dispose()


def apply_script(
    engine, database, replace_target=True, filename="20261015_CreateCaseSets.sql"
):
    script = (SQL_ROOT / "Migrations" / filename).read_text()
    if replace_target:
        script = script.replace(
            "DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';",
            f"DECLARE @ExpectedDatabase sysname = N'{database}';",
        )
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        # One batch, exactly as run in a DataGrip console.
        c.exec_driver_sql(script).close()


def test_datagrip_script_and_sqlserver_cohort_review_lifecycle(sql_database):
    engine, database = sql_database
    with Session(engine) as db:
        cohort = Cohort(
            UserId=1,
            Name="Existing cohort",
            Description="Existing data",
            Disease="",
            IsFacetDisplay=False,
            IsActive=True,
            LoadType="C",
            IsSolrUpdated=False,
            CreateBy="test",
        )
        db.add(cohort)
        db.flush()
        cohort_id = cohort.CohortId
        for case_id in (10, 10, 20):
            db.add(
                CohortCase(
                    CohortId=cohort_id,
                    CaseId=case_id,
                    IsActive=True,
                    LoadType="C",
                    IsSolrUpdated=False,
                    CreateBy="test",
                )
            )
        db.commit()
    apply_script(engine, database)
    with Session(engine) as db:
        case_set.require_schema(db)
        payload = CaseSetCreate(
            name="Review", sourceType="COHORT", sourceId=cohort_id, operationId=uuid4()
        )
        result = case_set.create(1, payload, db)
        assert result["captureState"] == "READY" and result["total"] == 2
        result = case_set.decide(
            result["caseSetId"],
            10,
            1,
            CaseSetDecision(state="EXCLUDED", revision=0),
            db,
        )
        assert result["set"]["excluded"] == 1
        assert case_set.list_sets(1, False, 1, 25, db)["total"] == 1
        assert db.query(CohortCase).count() == 3
        assert db.get(Cohort, cohort_id).Description == "Existing data"
    apply_script(engine, database)
    with engine.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM dbo.CaseSetCase")).scalar_one() == 2
        assert (
            c.execute(
                text("SELECT ReviewState FROM dbo.CaseSetCase WHERE CaseId=10")
            ).scalar_one()
            == "EXCLUDED"
        )


def test_wrong_database_and_incompatible_schema_abort_without_changes(sql_database):
    engine, database = sql_database
    with pytest.raises(DBAPIError, match="Wrong database"):
        apply_script(engine, database, replace_target=False)
    with engine.begin() as c:
        assert not inspect(c).has_table("CaseSet", schema="dbo")
        # Failure after creating CaseSet must roll that creation back.
        c.exec_driver_sql("CREATE TABLE dbo.CaseSetCase(OldPrototypeId int)")
    with pytest.raises(DBAPIError, match="incompatible dbo.CaseSetCase"):
        apply_script(engine, database)
    with engine.connect() as c:
        assert not inspect(c).has_table("CaseSet", schema="dbo")
        assert [
            column["name"]
            for column in inspect(c).get_columns("CaseSetCase", schema="dbo")
        ] == ["OldPrototypeId"]


def test_sqlserver_large_capture_and_concurrent_decisions(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        item = CaseSet(
            OwnerId=1,
            Name="Large set",
            SourceType="SAVED_SEARCH",
            SourceId=1,
            SourceName="Synthetic",
            SourceQuery=json.dumps({"query": "*:*", "now": 1}),
            CreationKey=str(uuid4()),
            CreationHash="test",
        )
        db.add(item)
        db.commit()
        set_id = item.CaseSetId
    index = SearchIndex()
    index.docs = [{"id": str(i), "caseid": i} for i in range(1, 1102)]
    cursor = "*"
    for _ in range(5):
        with Session(engine) as db:
            result = case_set.capture(set_id, 1, cursor, db, index)
        assert result["captureState"] != "FAILED", result
        if result["captureState"] == "READY":
            break
        cursor = result["captureCursor"]
    assert result["captureState"] == "READY" and result["total"] == 1101
    barrier = Barrier(2)

    def review(state):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            try:
                case_set.decide(
                    set_id, 1, 1, CaseSetDecision(state=state, revision=0), db
                )
                return 200
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(review, ("INCLUDED", "EXCLUDED")))
    assert sorted(outcomes) == [200, 409]


def test_sqlserver_operations_upgrade_large_sets_and_retries(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        left = ready_set(db, {i: "UNREVIEWED" for i in range(1, 1601)})
        right = ready_set(db, {i: "INCLUDED" for i in range(801, 2401)}, "B")
    # Simulate the first case-set release already installed with data.
    with engine.begin() as c:
        c.exec_driver_sql("ALTER TABLE dbo.CaseSet DROP CONSTRAINT CK_CaseSet_Source")
        c.exec_driver_sql(
            "ALTER TABLE dbo.CaseSet ADD CONSTRAINT CK_CaseSet_Source CHECK (SourceType IN ('SAVED_SEARCH','COHORT'))"
        )
    with Session(engine) as db:
        with pytest.raises(HTTPException) as error:
            case_set.operation_sources(1, db)
        assert error.value.status_code == 503
        assert case_set.list_sets(1, False, 1, 25, db)["total"] == 2
    upgrade = "20261015_EnableCaseSetOperations.sql"
    with pytest.raises(DBAPIError, match="Wrong database"):
        apply_script(engine, database, replace_target=False, filename=upgrade)
    apply_script(engine, database, filename=upgrade)
    apply_script(engine, database, filename=upgrade)
    with Session(engine) as db:
        assert db.query(CaseSetCase).count() == 3200
        for membership in ("NOT_EXCLUDED", "INCLUDED_ONLY"):
            a = set(range(1, 1601)) if membership == "NOT_EXCLUDED" else set()
            b = set(range(801, 2401))
            for operation, expected in (
                ("UNION", a | b),
                ("INTERSECTION", a & b),
                ("DIFFERENCE", a - b),
                ("SYMMETRIC_DIFFERENCE", a ^ b),
            ):
                request = CaseSetOperationPreview(
                    leftSetId=left,
                    rightSetId=right,
                    operation=operation,
                    membership=membership,
                )
                preview = case_set.preview_operation(1, request, db)
                assert preview["total"] == len(expected)
                payload = CaseSetOperationCreate(
                    **request.dict(),
                    name=operation,
                    leftRevision=preview["left"]["revision"],
                    rightRevision=preview["right"]["revision"],
                    operationId=uuid4(),
                )
                result = case_set.create_operation(1, payload, db)
                assert result["total"] == result["unreviewed"] == len(expected)
                rows = (
                    db.query(CaseSetCase)
                    .filter_by(CaseSetId=result["caseSetId"])
                    .order_by(CaseSetCase.Ordinal)
                    .all()
                )
                assert [r.CaseId for r in rows] == sorted(expected)
                assert (
                    case_set.create_operation(1, payload, db)["caseSetId"]
                    == result["caseSetId"]
                )
        assert db.get(CaseSet, left).Revision == db.get(CaseSet, right).Revision == 0
    # Updated installer must preserve OPERATION rows on subsequent runs too.
    apply_script(engine, database)
    with Session(engine) as db:
        assert db.query(CaseSet).count() == 10


def test_sqlserver_concurrent_operation_retry_and_review(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        left = ready_set(db, {1: "UNREVIEWED", 2: "INCLUDED"})
        right = ready_set(db, {2: "INCLUDED", 3: "INCLUDED"}, "B")
    payload = CaseSetOperationCreate(
        leftSetId=left,
        rightSetId=right,
        operation="UNION",
        name="Union",
        leftRevision=0,
        rightRevision=0,
        operationId=uuid4(),
    )
    barrier = Barrier(2)

    def save(_):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return case_set.create_operation(1, payload, db)["caseSetId"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save, range(2)))
    assert results[0] == results[1]
    with Session(engine) as db:
        assert db.query(CaseSet).count() == 3

    # The creation either wins the parent lock and captures old membership, or
    # detects the committed review and refuses the stale preview. Never mix them.
    payload.operationId = uuid4()
    barrier = Barrier(2)

    def competing(action):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            if action == "review":
                case_set.decide(
                    left, 1, 1, CaseSetDecision(state="EXCLUDED", revision=0), db
                )
                return "reviewed"
            try:
                return case_set.create_operation(1, payload, db)["total"]
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        result, reviewed = list(pool.map(competing, ("save", "review")))
    assert reviewed == "reviewed" and result in (3, 409)


@pytest.mark.parametrize("upgraded", [False, True])
def test_operations_with_dml_permissions_and_hidden_constraint_definition(
    sql_database, upgraded
):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        left = ready_set(db, {1: "UNREVIEWED", 2: "INCLUDED"})
        right = ready_set(db, {2: "INCLUDED", 3: "INCLUDED"}, "B")
    with engine.begin() as c:
        c.exec_driver_sql("CREATE USER case_set_api WITHOUT LOGIN")
        c.exec_driver_sql("ALTER ROLE db_datareader ADD MEMBER case_set_api")
        c.exec_driver_sql("ALTER ROLE db_datawriter ADD MEMBER case_set_api")
        if not upgraded:
            c.exec_driver_sql(
                "ALTER TABLE dbo.CaseSet DROP CONSTRAINT CK_CaseSet_Source"
            )
            c.exec_driver_sql(
                "ALTER TABLE dbo.CaseSet ADD CONSTRAINT CK_CaseSet_Source CHECK (SourceType IN ('SAVED_SEARCH','COHORT'))"
            )

    @contextmanager
    def api_session():
        with engine.connect() as c:
            c.exec_driver_sql("EXECUTE AS USER = 'case_set_api'")
            c.commit()
            try:
                with Session(c) as db:
                    yield db
            finally:
                c.rollback()
                c.exec_driver_sql("REVERT")
                c.commit()

    request = CaseSetOperationPreview(
        leftSetId=left, rightSetId=right, operation="UNION"
    )
    payload = CaseSetOperationCreate(
        **request.dict(),
        name="Restricted account union",
        leftRevision=0,
        rightRevision=0,
        operationId=uuid4(),
    )
    with api_session() as db:
        constraint = db.execute(
            text(
                "SELECT definition FROM sys.check_constraints WHERE name='CK_CaseSet_Source'"
            )
        ).one()
        assert constraint.definition is None
        assert (
            db.execute(
                text(
                    "SELECT HAS_PERMS_BY_NAME(N'dbo.CaseSet', N'OBJECT', N'VIEW DEFINITION')"
                )
            ).scalar_one()
            == 0
        )
        case_set.require_schema(db)
        assert len(case_set.operation_sources(1, db)) == 2
        assert case_set.preview_operation(1, request, db)["total"] == 3
        if upgraded:
            result = case_set.create_operation(1, payload, db)
            assert result["total"] == 3 and result["sourceType"] == "OPERATION"
            assert (
                case_set.create_operation(1, payload, db)["caseSetId"]
                == result["caseSetId"]
            )
        else:
            with pytest.raises(HTTPException) as error:
                case_set.create_operation(1, payload, db)
            assert error.value.status_code == 503
            assert "database update" in error.value.detail
            assert db.query(CaseSet).count() == 2
            assert db.query(CaseSetCase).count() == 4
    if not upgraded:
        apply_script(engine, database, filename="20261015_EnableCaseSetOperations.sql")
        with api_session() as db:
            # The same request succeeds after migration without extra privileges.
            assert case_set.create_operation(1, payload, db)["total"] == 3


@pytest.mark.parametrize("can_delete", [False, True])
def test_sqlserver_delete_with_reader_writer_permissions_is_atomic(
    sql_database, can_delete
):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        target = ready_set(db, {i: "INCLUDED" for i in range(1, 1201)})
        other = ready_set(db, {1: "EXCLUDED"}, "Keep")
    with engine.begin() as c:
        c.exec_driver_sql("CREATE USER case_set_delete_api WITHOUT LOGIN")
        c.exec_driver_sql("ALTER ROLE db_datareader ADD MEMBER case_set_delete_api")
        c.exec_driver_sql("ALTER ROLE db_datawriter ADD MEMBER case_set_delete_api")
        if not can_delete:
            # Child deletion succeeds, then the denied parent delete must roll it back.
            c.exec_driver_sql("DENY DELETE ON dbo.CaseSet TO case_set_delete_api")
    with engine.connect() as c:
        c.exec_driver_sql("EXECUTE AS USER = 'case_set_delete_api'")
        c.commit()
        try:
            with Session(c) as db:
                if can_delete:
                    case_set.delete_set(target, 1, 0, db)
                else:
                    with pytest.raises(DBAPIError):
                        case_set.delete_set(target, 1, 0, db)
        finally:
            c.rollback()
            c.exec_driver_sql("REVERT")
            c.commit()
    with Session(engine) as db:
        assert (db.get(CaseSet, target) is None) == can_delete
        assert case_set.counts(target, db)["total"] == (0 if can_delete else 1200)
        assert db.get(CaseSetCase, (other, 1)).ReviewState == "EXCLUDED"


def test_sqlserver_delete_serializes_with_concurrent_review(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        target = ready_set(db, {1: "UNREVIEWED"})
    barrier = Barrier(2)

    def perform(action):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            try:
                if action == "delete":
                    case_set.delete_set(target, 1, 0, db)
                    return 204
                case_set.decide(
                    target, 1, 1, CaseSetDecision(state="INCLUDED", revision=0), db
                )
                return 200
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcome = tuple(pool.map(perform, ("delete", "review")))
    assert outcome in ((204, 404), (409, 200))
    with Session(engine) as db:
        assert (db.get(CaseSet, target) is None) == (outcome[0] == 204)
        assert case_set.counts(target, db)["total"] == (0 if outcome[0] == 204 else 1)


def test_sqlserver_specimen_migration_permissions_and_atomic_deletion(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    # Simulate an existing installation before specimen selection was added.
    with engine.begin() as c:
        c.exec_driver_sql("DROP TABLE dbo.CaseSetSpecimen")
        c.exec_driver_sql(
            "CREATE TABLE dbo.Specimen(SpecimenId INT PRIMARY KEY, CaseId INT, SpecimenNumber NVARCHAR(100), IsActive BIT)"
        )
        c.exec_driver_sql(
            "INSERT dbo.Specimen VALUES(101,1,'S26-1 A',1),(102,1,'S26-1 B',1),(201,2,'S26-2 A',1)"
        )
    upgrade = "20261015_AddCaseSetSpecimens.sql"
    with pytest.raises(DBAPIError, match="Wrong database"):
        apply_script(engine, database, replace_target=False, filename=upgrade)
    apply_script(engine, database, filename=upgrade)
    with Session(engine) as db:
        target = ready_set(db, {1: "UNREVIEWED"})
        other = ready_set(db, {1: "UNREVIEWED"}, "Keep")
    with engine.begin() as c:
        c.exec_driver_sql("CREATE USER specimen_api WITHOUT LOGIN")
        c.exec_driver_sql("ALTER ROLE db_datareader ADD MEMBER specimen_api")
        c.exec_driver_sql("ALTER ROLE db_datawriter ADD MEMBER specimen_api")
    with engine.connect() as c:
        c.exec_driver_sql("EXECUTE AS USER = 'specimen_api'")
        c.commit()
        try:
            with Session(c) as db:
                case_set.require_specimen_schema(db)
                payload = CaseSetSpecimenSelection(specimenIds=[101, 102], revision=0)
                response = case_set.select_specimens(target, 1, 1, payload, db)
                assert response["member"]["revision"] == 1
                assert sum(s["selected"] for s in response["specimens"]) == 2
                assert (
                    case_set.select_specimens(target, 1, 1, payload, db)["member"][
                        "revision"
                    ]
                    == 1
                )
        finally:
            c.rollback()
            c.exec_driver_sql("REVERT")
            c.commit()
    apply_script(engine, database, filename=upgrade)
    apply_script(engine, database)
    with Session(engine) as db:
        assert db.query(CaseSetSpecimen).count() == 2
        assert not any(
            s["selected"] for s in case_set.specimens(other, 1, 1, db)["specimens"]
        )
    # A failure deleting the parent must restore the specimen and membership rows.
    with engine.begin() as c:
        c.exec_driver_sql("DENY DELETE ON dbo.CaseSet TO specimen_api")
    with engine.connect() as c:
        c.exec_driver_sql("EXECUTE AS USER = 'specimen_api'")
        c.commit()
        try:
            with Session(c) as db:
                with pytest.raises(DBAPIError):
                    case_set.delete_set(target, 1, 1, db)
        finally:
            c.rollback()
            c.exec_driver_sql("REVERT")
            c.commit()
    with Session(engine) as db:
        assert db.query(CaseSetSpecimen).count() == 2
        assert db.get(CaseSetCase, (target, 1)) is not None
        case_set.delete_set(target, 1, 1, db)
        assert db.query(CaseSetSpecimen).count() == 0
        assert db.get(CaseSet, other) is not None
        assert db.execute(text("SELECT COUNT(*) FROM dbo.Specimen")).scalar_one() == 3


def test_sqlserver_specimen_changes_serialize_with_review(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with engine.begin() as c:
        c.exec_driver_sql(
            "CREATE TABLE dbo.Specimen(SpecimenId INT PRIMARY KEY, CaseId INT, SpecimenNumber NVARCHAR(100), IsActive BIT)"
        )
        c.exec_driver_sql("INSERT dbo.Specimen VALUES(101,1,'S26-1 A',1)")
    with Session(engine) as db:
        target = ready_set(db, {1: "UNREVIEWED"})
    barrier = Barrier(2)

    def perform(action):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            try:
                if action == "specimens":
                    case_set.select_specimens(
                        target,
                        1,
                        1,
                        CaseSetSpecimenSelection(specimenIds=[101], revision=0),
                        db,
                    )
                else:
                    case_set.decide(
                        target, 1, 1, CaseSetDecision(state="INCLUDED", revision=0), db
                    )
                return 200
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(perform, ("specimens", "review")))
    assert sorted(outcomes) == [200, 409]
    with Session(engine) as db:
        assert db.get(CaseSetCase, (target, 1)).Revision == 1
        assert db.query(CaseSetSpecimen).count() == (1 if outcomes[0] == 200 else 0)


def test_specimen_migration_rejects_incompatible_table(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with engine.begin() as c:
        c.exec_driver_sql("DROP TABLE dbo.CaseSetSpecimen")
        c.exec_driver_sql("CREATE TABLE dbo.CaseSetSpecimen(OldId INT)")
    with pytest.raises(DBAPIError, match="incompatible dbo.CaseSetSpecimen"):
        apply_script(engine, database, filename="20261015_AddCaseSetSpecimens.sql")
    with engine.connect() as c:
        assert [
            column["name"]
            for column in inspect(c).get_columns("CaseSetSpecimen", schema="dbo")
        ] == ["OldId"]


def test_cart_migration_retry_and_concurrent_additions(sql_database):
    engine, database = sql_database
    apply_script(engine, database)
    with Session(engine) as db:
        set_id = ready_set(db, {1: "EXCLUDED"})
    with engine.begin() as c:
        c.exec_driver_sql("ALTER TABLE dbo.CaseSet DROP CONSTRAINT CK_CaseSet_Source")
        c.exec_driver_sql(
            "ALTER TABLE dbo.CaseSet ADD CONSTRAINT CK_CaseSet_Source CHECK (SourceType IN ('SAVED_SEARCH','COHORT','OPERATION'))"
        )
    payload = CaseSetCartCreate(name="Cart", caseIds=[3, 2, 3], operationId=uuid4())
    with Session(engine) as db:
        with pytest.raises(HTTPException, match="database update"):
            case_set.create_from_cart(1, payload, db, SearchIndex())
    for _ in range(2):
        apply_script(engine, database, filename="20261021_EnableCaseSetCart.sql")
    with Session(engine) as db:
        created = case_set.create_from_cart(1, payload, db, SearchIndex())
        retry = case_set.create_from_cart(1, payload, db, SearchIndex())
        assert created["caseSetId"] == retry["caseSetId"]
        assert created["total"] == created["unreviewed"] == 2
    barrier = Barrier(2)

    def add(ids):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return case_set.add_cases(
                set_id, 1, CaseSetAddCases(caseIds=ids), db, SearchIndex()
            )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(add, [[1, 2, 3], [2, 4]]))
    assert sum(item["added"] for item in results) == 3
    with Session(engine) as db:
        rows = db.query(CaseSetCase).filter_by(CaseSetId=set_id).all()
        assert {row.CaseId for row in rows} == {1, 2, 3, 4}
        assert len({row.Ordinal for row in rows}) == 4
        assert db.get(CaseSetCase, (set_id, 1)).ReviewState == "EXCLUDED"


def test_teaching_migration_upgrades_private_defaults_and_preserves_publication(
    sql_database,
):
    from viewmodel.case_set import CaseSetSharing

    engine, database = sql_database
    script = (SQL_ROOT / "Migrations" / "20261015_CreateCaseSets.sql").read_text()
    # Recreate the installed pre-sharing schema, then apply the dedicated upgrade.
    script = script.replace("\t[IsPublic] BIT NOT NULL DEFAULT 0,\n", "")
    script = script.replace("\t[SpecialtyCategory] NVARCHAR(100) NULL, ", "")
    start = script.index("-- Sharing upgrades are additive")
    end = script.index("    COMMIT TRANSACTION;", start)
    script = script[:start] + script[end:]
    script = script.replace(
        "DECLARE @ExpectedDatabase sysname = N'PIRO_DEV';",
        f"DECLARE @ExpectedDatabase sysname = N'{database}';",
    )
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        c.exec_driver_sql(script).close()
        c.exec_driver_sql(
            "CREATE TABLE dbo.Specialty(SpecialtyCategory varchar(100), IsActive bit); INSERT dbo.Specialty VALUES('GI',1),('Derm',1)"
        )
        c.exec_driver_sql(
            "INSERT dbo.CaseSet(OwnerId,Name,SourceType,SourceId,SourceName,CreationKey,CreationHash,CaptureState) VALUES(1,N'Teaching','COHORT',1,N'Original','teaching-test','hash','READY')"
        )
        c.exec_driver_sql(
            "INSERT dbo.CaseSetCase(CaseSetId,CaseId,Ordinal,ReviewState) SELECT CaseSetId,7,1,'INCLUDED' FROM dbo.CaseSet"
        )
    apply_script(engine, database, filename="20261021_EnableTeachingSets.sql")
    with Session(engine) as db:
        case_set.require_schema(db)
        item = db.query(CaseSet).one()
        assert item.IsPublic is False and item.SpecialtyCategory is None
        sid = item.CaseSetId
        result = case_set.share(
            sid,
            1,
            CaseSetSharing(isPublic=True, specialtyCategory="GI", revision=0),
            db,
        )
        assert result["isPublic"] is True and result["included"] == 1
    apply_script(engine, database, filename="20261021_EnableTeachingSets.sql")
    apply_script(engine, database)
    with Session(engine) as db:
        item = db.get(CaseSet, sid)
        assert item.IsPublic is True and item.SpecialtyCategory == "GI"
        assert db.get(CaseSetCase, (sid, 7)).ReviewState == "INCLUDED"
