import json

import pytest
from apis.external_api.admin import main
from apis.external_api.models import audits, keys
from sqlalchemy import select

from tests.external_api.types import ApiFixture


def test_cli_lists_metadata_without_disclosing_keys_and_audits_changes(
    api: ApiFixture,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify cli lists metadata without disclosing keys and audits changes."""
    monkeypatch.setattr(
        "apis.external_api.admin.create_database_engine",
        lambda **_options: api["engine"],
    )
    monkeypatch.setattr(api["engine"], "dispose", lambda: None)
    assert main(["list-keys", "--client-id", api["client_id"]]) == 0
    output = capsys.readouterr().out
    assert "SecretHash" not in output
    assert "api_key" not in output
    assert api["credential"]["api_key"] not in output
    assert (
        main(
            ["issue-key", "--client-id", api["client_id"], "--actor", "tester"]
        )
        == 0
    )
    issued = json.loads(capsys.readouterr().out)
    assert issued["api_key"].startswith("piro_")
    assert (
        main(["revoke-key", "--key-id", issued["key_id"], "--actor", "tester"])
        == 0
    )
    capsys.readouterr()
    with api["engine"].connect() as connection:
        assert (
            connection.scalar(
                select(keys.c.RevokedAt).where(
                    keys.c.KeyId == issued["key_id"]
                )
            )
            is not None
        )
        events = connection.execute(
            select(audits.c.Event, audits.c.Actor)
        ).all()
        assert ("key_revoked", "tester") in events
