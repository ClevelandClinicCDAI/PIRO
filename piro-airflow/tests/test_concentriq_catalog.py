"""Catalog query and transaction behavior, without Airflow or live databases."""

import sys
import ast
from pathlib import Path
from unittest.mock import Mock
from types import ModuleType

import pytest
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks.loaders import concentriq_case_loader as module
from tasks.utils import concentriq_setup


@pytest.fixture(autouse=True)
def isolated_limit_settings(monkeypatch):
    # Tests must not inherit a developer's .env or Airflow configuration.
    monkeypatch.setattr(concentriq_setup, "load_dotenv", Mock())
    monkeypatch.delenv("CONCENTRIQ_MAX_CASES", raising=False)
    monkeypatch.delenv("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES", raising=False)
    sdk = ModuleType("airflow.sdk")
    sdk.Variable = Mock()
    sdk.Variable.get.side_effect = lambda name, default=None: default
    monkeypatch.setitem(sys.modules, "airflow.sdk", sdk)
    return sdk.Variable


@pytest.fixture
def loader(monkeypatch):
    instance = module.ConcentriqCaseLoader.__new__(module.ConcentriqCaseLoader)
    instance._piro_db_session = Mock()
    instance._piro_db_session.execute.return_value.scalar_one.return_value = 0
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


@pytest.mark.parametrize("configured,expected", [("0", None), ("1", 1),
                                                 ("2501", 2501)])
def test_limit_from_local_environment(monkeypatch, configured, expected):
    monkeypatch.setenv("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES", configured)
    assert concentriq_setup.get_concentriq_max_cases() == expected
    concentriq_setup.load_dotenv.assert_called_once_with(
        Path(concentriq_setup.__file__).resolve().parents[2] / ".env"
    )


def test_limit_from_airflow_variable(isolated_limit_settings):
    isolated_limit_settings.get.side_effect = None
    isolated_limit_settings.get.return_value = "17"
    assert concentriq_setup.get_concentriq_max_cases() == 17
    isolated_limit_settings.get.assert_called_once_with(
        "CONCENTRIQ_MAX_CASES", default="0"
    )


def test_project_dotenv_is_loaded_outside_project_directory(monkeypatch, tmp_path):
    project = tmp_path / "piro-airflow"
    project.mkdir()
    (project / ".env").write_text("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES=11\n")
    monkeypatch.setattr(concentriq_setup, "__file__",
                        str(project / "tasks/utils/concentriq_setup.py"))
    monkeypatch.setattr(concentriq_setup, "load_dotenv", load_dotenv)
    monkeypatch.chdir(tmp_path)
    assert concentriq_setup.get_concentriq_max_cases() == 11
    monkeypatch.setenv("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES", "7")
    assert concentriq_setup.get_concentriq_max_cases() == 7


def test_missing_limit_defaults_to_unlimited():
    assert concentriq_setup.get_concentriq_max_cases() is None


def test_limit_without_airflow(monkeypatch):
    monkeypatch.setitem(sys.modules, "airflow.sdk", None)
    assert concentriq_setup.get_concentriq_max_cases() is None
    monkeypatch.setenv("CONCENTRIQ_MAX_CASES", "5")
    assert concentriq_setup.get_concentriq_max_cases() == 5


@pytest.mark.parametrize("explicit,expected", [(2, 2), (0, None)])
def test_explicit_limit_overrides_configuration(monkeypatch, explicit, expected):
    monkeypatch.setenv("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES", "17")
    assert concentriq_setup.get_concentriq_max_cases(explicit) == expected


@pytest.mark.parametrize("value", ["-1", "1.5", "abc", -1, 1.5, True])
def test_invalid_limit_fails_before_database_access(loader, monkeypatch, value):
    instance, engine = loader
    if isinstance(value, str):
        monkeypatch.setenv("AIRFLOW_VAR_CONCENTRIQ_MAX_CASES", value)
        value = None
    with pytest.raises(ValueError, match="non-negative integer"):
        instance.get_concentriq_data(value)
    instance._piro_db_session.execute.assert_not_called()
    engine.connect.assert_not_called()


@pytest.mark.parametrize("limit,count,full_snapshot,next_id", [
    (2, 2, False, 22), (3, 2, False, 0), (0, 2, True, 0),
])
def test_loader_passes_limit_and_saves_progress(
    loader, monkeypatch, limit, count, full_snapshot, next_id
):
    instance, engine = loader
    instance._piro_db_session.execute.return_value.scalar_one.return_value = 20
    batches = Mock(return_value=iter([[{
        "id": 21 + i, "accessionId": f"TEST-{21 + i}", "accessionDate": None
    } for i in range(count)]]))
    monkeypatch.setattr(module, "iter_catalog_batches", batches)
    instance.get_concentriq_data(limit)
    batches.assert_called_once_with(engine, 1000, limit or None, 20 if limit else 0)
    finalize = next(call for call in instance._piro_db_session.execute.call_args_list
                    if "@finalize=1" in str(call.args[0]))
    assert finalize.args[1] == {
        "full_snapshot": full_snapshot, "last_case_id": next_id,
    }
    instance._piro_db_session.commit.assert_called_once()
    engine.dispose.assert_called_once()


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
