"""Opt-in tests against disposable local PostgreSQL and SQL Server databases.

Set CONCENTRIQ_TEST_POSTGRES_URL and CONCENTRIQ_TEST_SQLSERVER_URL to empty
databases named concentriq_limit_test on localhost. No production data is used.
"""

import os
import re
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks.loaders import concentriq_case_loader as module
from tasks.loaders.concentriq_catalog import iter_catalog_batches


@pytest.fixture
def databases(monkeypatch):
    urls = [os.getenv(f"CONCENTRIQ_TEST_{name}_URL")
            for name in ("POSTGRES", "SQLSERVER")]
    if not all(urls):
        pytest.skip("Disposable database URLs are not configured")
    for value in urls:
        url = make_url(value)
        assert url.host in ("localhost", "127.0.0.1")
        assert url.database == "concentriq_limit_test"
    source, piro = [create_engine(url, hide_parameters=True) for url in urls]
    root = Path(__file__).resolve().parents[2]
    try:
        with source.begin() as connection:
            connection.execute(text("""
                CREATE TABLE public.case_details
                    (id int PRIMARY KEY, accession_id text, accession_date timestamp);
                CREATE TABLE public.slides (id int PRIMARY KEY, case_detail_id int);
                CREATE TABLE public.images (id int PRIMARY KEY, slide_id int, status text);
                INSERT INTO public.case_details
                    SELECT id, 'TEST-' || id, NULL FROM generate_series(10, 70, 10) id;
                INSERT INTO public.case_details VALUES (15, 'NOT-READY', NULL),
                                                       (25, 'NO-IMAGES', NULL);
                INSERT INTO public.slides SELECT id, id FROM public.case_details;
                INSERT INTO public.images
                    SELECT id, id, CASE WHEN id = 15 THEN 'pending' ELSE 'ready' END
                    FROM public.case_details WHERE id <> 25;
            """))
        with piro.begin() as connection:
            connection.execute(text("""
                CREATE TABLE dbo.[Case] (CaseId int PRIMARY KEY, CaseNumber varchar(100));
                CREATE TABLE dbo.CaseSolr (CaseId int PRIMARY KEY, IsConcentriq bit,
                    CaseConcentriqId int, IsSolrUpdate bit);
                CREATE TABLE dbo.CaseSolr_Delta (CaseId int PRIMARY KEY, IsConcentriq bit,
                    CaseConcentriqId int, IsSolrUpdate bit, Action char(1), CurrentDate datetime);
                INSERT INTO dbo.[Case] VALUES (10, 'TEST-10'), (20, 'TEST-20'),
                    (30, 'TEST-30'), (40, 'TEST-40'), (50, 'TEST-50'),
                    (60, 'TEST-60'), (70, 'TEST-70');
                INSERT INTO dbo.CaseSolr SELECT CaseId, 0, -1, 0 FROM dbo.[Case];
            """))
            paths = [root / "piro-sql/Table" / f"dbo.{name}.Table.sql"
                     for name in ("ConcentriqCase", "ConcentriqConfig")]
            paths += [root / "piro-sql/Airflow/PROCS" /
                      f"dbo.P_AIRFLOW_Concentriq_Case_{name}.StoredProcedure.sql"
                      for name in ("Load", "Sync", "Delete")]
            for path in paths:
                for batch in re.split(r"(?im)^GO\s*$", path.read_text()):
                    if batch.strip():
                        connection.exec_driver_sql(batch)
        monkeypatch.setattr(module, "get_concentriq_db_engine", lambda: source)
        monkeypatch.setattr(module, "get_concentriq_case_page_size", lambda: 2)
        yield source, piro
    finally:
        source.dispose()
        piro.dispose()


def test_progressive_limits_and_atomic_retries(databases):
    source, piro = databases

    def ids(limit, after=0):
        return [item["id"] for batch in iter_catalog_batches(source, 2, limit, after)
                for item in batch]

    assert ids(1) == [10]
    assert ids(3) == [10, 20, 30]  # Limit also applies across fetch batches.
    assert ids(3, 30) == [40, 50, 60]
    assert ids(3, 70) == [10, 20, 30]  # Exact-size end of a pass wraps.
    assert ids(None) == [10, 20, 30, 40, 50, 60, 70]

    def run(limit):
        loader = module.ConcentriqCaseLoader(piro_engine=piro)
        try:
            loader.get_concentriq_data(limit)
        finally:
            loader.close_db_connection()

    def state():
        with piro.connect() as connection:
            active = list(connection.execute(text("""
                SELECT ConcentriqCaseId FROM dbo.ConcentriqCase
                WHERE IsActive = 1 ORDER BY ConcentriqCaseId
            """)).scalars())
            checkpoint = connection.execute(text("""
                SELECT [Value] FROM dbo.ConcentriqConfig
                WHERE [Key] = 'CaseDetails.Get.LastCaseId'
            """)).scalar_one()
            return active, int(checkpoint)

    run(3)
    assert state() == ([10, 20, 30], 30)
    # A later source batch fails after the earlier batch has been staged.
    with source.begin() as connection:
        connection.execute(text("UPDATE public.case_details SET accession_id = '' WHERE id = 60"))
    with pytest.raises(ValueError, match="Invalid Concentriq accession"):
        run(3)
    assert state() == ([10, 20, 30], 30)
    with source.begin() as connection:
        connection.execute(text("UPDATE public.case_details SET accession_id = 'TEST-60' WHERE id = 60"))
    run(3)
    assert state() == ([10, 20, 30, 40, 50, 60], 60)
    run(3)
    assert state() == ([10, 20, 30, 40, 50, 60, 70], 0)
    # Limited refresh preserves other records even if their images disappear.
    with source.begin() as connection:
        connection.execute(text("UPDATE public.images SET status = 'pending' WHERE id = 70"))
    run(3)
    assert state() == ([10, 20, 30, 40, 50, 60, 70], 30)
    # Unlimited refresh ignores progress, deactivates missing cases, and resets progress.
    run(0)
    assert state() == ([10, 20, 30, 40, 50, 60], 0)
    with piro.connect() as connection:
        assert connection.execute(text(
            "SELECT IsConcentriq FROM dbo.CaseSolr WHERE CaseId = 70"
        )).scalar_one() is False
        assert connection.execute(text(
            "SELECT COUNT(*) FROM dbo.CaseSolr_Delta"
        )).scalar_one() == 7
    # Two exact-size slices cycle back to the beginning, without a no-op run.
    run(3)
    run(3)
    assert state()[1] == 60
    run(3)
    assert state()[1] == 30
    # Empty catalogs fail without deleting records or advancing progress.
    with source.begin() as connection:
        connection.execute(text("UPDATE public.images SET status = 'pending'"))
    with pytest.raises(ValueError, match="Empty Concentriq"):
        run(3)
    assert state() == ([10, 20, 30, 40, 50, 60], 30)
    loader = module.ConcentriqCaseLoader(piro_engine=piro)
    try:
        loader.delete_concentriq_case_data()
    finally:
        loader.close_db_connection()
    assert state() == ([], 0)
