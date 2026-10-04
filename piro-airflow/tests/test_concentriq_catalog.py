"""Catalog query and transaction behavior, without Airflow or live databases."""

import sys
import ast
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks.loaders import concentriq_case_loader as module
from tasks.utils import concentriq_setup


@pytest.fixture
def loader(monkeypatch):
    instance = module.ConcentriqCaseLoader.__new__(module.ConcentriqCaseLoader)
    instance._piro_db_session = Mock()
    engine = Mock()
    monkeypatch.setattr(module, "get_concentriq_db_engine", lambda: engine)
    monkeypatch.setattr(module, "get_concentriq_case_page_size", lambda: 1000)
    return instance, engine


def test_failed_later_batch_never_publishes(loader, monkeypatch):
    instance, engine = loader

    def batches(*args):
        yield [{"id": 1, "accessionId": "TEST-1", "accessionDate": None}]
        raise RuntimeError("source disconnected")

    monkeypatch.setattr(module, "iter_catalog_batches", batches)
    with pytest.raises(RuntimeError):
        instance.get_concentriq_data()
    instance._piro_db_session.rollback.assert_called_once()
    instance._piro_db_session.commit.assert_not_called()
    assert all("@finalize" not in str(call.args[0])
               for call in instance._piro_db_session.execute.call_args_list)
    engine.dispose.assert_called_once()


def test_empty_catalog_retains_existing_data(loader, monkeypatch):
    instance, _ = loader
    monkeypatch.setattr(module, "iter_catalog_batches", lambda *args: iter([]))
    with pytest.raises(ValueError, match="Empty Concentriq"):
        instance.get_concentriq_data()
    instance._piro_db_session.commit.assert_not_called()
    instance._piro_db_session.rollback.assert_called_once()


@pytest.mark.parametrize("value,enabled", [(None, False), ("false", False),
                                           ("0", False), ("1", True), ("TRUE", True)])
def test_enable_flag_respects_value(loader, value, enabled):
    instance, _ = loader
    instance._piro_db_session.execute.return_value.scalar.return_value = value
    assert instance.should_we_process_concentriq_data() is enabled


def test_postgres_settings_escape_credentials_and_split_port(monkeypatch):
    values = {"POSTGRES_SERVER": "catalog.local,5439", "POSTGRES_DATABASE": "dx",
              "POSTGRES_USER": "reader", "POSTGRES_PASSWORD": "p@ss:/word",
              "CONCENTRIQ_DB_SSLMODE": "prefer"}
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    engine = concentriq_setup.get_concentriq_db_engine()
    try:
        assert engine.url.host == "catalog.local"
        assert engine.url.port == 5439
        assert engine.url.database == "dx"
        assert engine.url.password == values["POSTGRES_PASSWORD"]
        assert values["POSTGRES_PASSWORD"] not in str(engine.url)
    finally:
        engine.dispose()


def test_solr_upload_includes_single_pending_case():
    # Load the real upload method without unrelated Airflow and HTTP setup.
    source = Path(__file__).resolve().parents[1] / "tasks/loaders/solr_case_data_loader.py"
    tree = ast.parse(source.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == "upload_records_to_solr")
    standalone = ast.Module(body=[method], type_ignores=[])
    namespace = {"logger": Mock()}
    exec(compile(standalone, str(source), "exec"), namespace)
    uploader = Mock()
    uploader._get_case_data_key_min.return_value = 42
    uploader._get_case_data.return_value = None
    uploader.batch_size = 1000
    assert namespace["upload_records_to_solr"](uploader) is True
    uploader._get_case_data.assert_called_once_with(41, 1000)
