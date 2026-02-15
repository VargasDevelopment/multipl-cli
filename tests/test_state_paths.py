from __future__ import annotations

from pathlib import Path

from multipl_cli import polling_lock, state
from multipl_cli.config import claims_path, config_dir, config_path


def test_state_paths_use_multipl_cli_home_override(monkeypatch, tmp_path: Path) -> None:
    override_home = tmp_path / "agent-01"
    monkeypatch.setenv(state.MULTIPL_CLI_HOME_ENV_VAR, str(override_home))

    assert state.get_state_dir() == override_home
    assert config_dir() == override_home
    assert config_path() == override_home / "config.json"
    assert claims_path() == override_home / "claims.json"
    assert (
        polling_lock.acquire_loop_lock_path("abc123")
        == override_home / "locks" / "claim-acquire-abc123.lock"
    )


def test_different_multipl_cli_home_values_produce_different_lock_paths(
    monkeypatch, tmp_path: Path
) -> None:
    home_one = tmp_path / "worker-01"
    home_two = tmp_path / "worker-02"

    monkeypatch.setenv(state.MULTIPL_CLI_HOME_ENV_VAR, str(home_one))
    first = polling_lock.acquire_loop_lock_path("same-key")

    monkeypatch.setenv(state.MULTIPL_CLI_HOME_ENV_VAR, str(home_two))
    second = polling_lock.acquire_loop_lock_path("same-key")

    assert first != second
    assert first.name == second.name == "claim-acquire-same-key.lock"


def test_default_state_path_behavior_is_unchanged_without_override(monkeypatch) -> None:
    monkeypatch.delenv(state.MULTIPL_CLI_HOME_ENV_VAR, raising=False)
    monkeypatch.setattr(state, "user_config_dir", lambda _app, _author: "/tmp/multipl-default")

    expected = Path("/tmp/multipl-default")
    assert state.get_state_dir() == expected
    assert config_dir() == expected
    assert config_path() == expected / "config.json"
