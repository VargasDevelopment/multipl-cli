from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import whoami
from multipl_cli.config import Config, Profile, resolve_poster_api_key, resolve_worker_api_key


@dataclass
class _FakeResponse:
    status_code: int
    parsed: object | None = None


@dataclass
class _FakeWorker:
    id: str = "worker_123"
    name: str = "worker"
    is_claimed: bool = True
    claimed_by_poster_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "isClaimed": self.is_claimed,
            "claimedByPosterId": self.claimed_by_poster_id,
        }


@dataclass
class _FakeWorkerMe:
    worker: _FakeWorker


@dataclass
class _FakeMetrics:
    payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={"default": Profile(name="default")},
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_worker_whoami_uses_multipl_worker_key_override(monkeypatch) -> None:
    monkeypatch.setenv("MULTIPL_WORKER_KEY", "wk_env_override")
    monkeypatch.delenv("MULTIPL_POSTER_KEY", raising=False)

    captured_keys: list[str | None] = []
    monkeypatch.setattr(whoami, "ensure_client_available", lambda: None)
    monkeypatch.setattr(
        whoami,
        "build_client",
        lambda _base_url, api_key=None: captured_keys.append(api_key) or object(),
    )
    monkeypatch.setattr(
        whoami,
        "get_worker_me",
        lambda **_kwargs: _FakeResponse(status_code=200, parsed=_FakeWorkerMe(worker=_FakeWorker())),
    )
    monkeypatch.setattr(
        whoami,
        "get_worker_metrics",
        lambda **_kwargs: _FakeResponse(status_code=200, parsed=_FakeMetrics({"jobsCompleted": 1})),
    )
    monkeypatch.setattr(
        whoami,
        "get_poster_metrics",
        lambda **_kwargs: _FakeResponse(status_code=403, parsed=None),
    )

    state = _state()
    runner = CliRunner()
    result = runner.invoke(whoami.app, ["--json"], obj=state)

    assert result.exit_code == 0
    assert captured_keys == ["wk_env_override"]
    assert state.config.get_active_profile().worker_api_key is None


def test_poster_whoami_uses_multipl_poster_key_override(monkeypatch) -> None:
    monkeypatch.setenv("MULTIPL_POSTER_KEY", "pk_env_override")
    monkeypatch.delenv("MULTIPL_WORKER_KEY", raising=False)

    captured_keys: list[str | None] = []
    monkeypatch.setattr(whoami, "ensure_client_available", lambda: None)
    monkeypatch.setattr(
        whoami,
        "build_client",
        lambda _base_url, api_key=None: captured_keys.append(api_key) or object(),
    )
    monkeypatch.setattr(
        whoami,
        "get_poster_metrics",
        lambda **_kwargs: _FakeResponse(
            status_code=200,
            parsed=_FakeMetrics({"jobsUnlockedAllTime": 1}),
        ),
    )
    monkeypatch.setattr(
        whoami,
        "get_worker_me",
        lambda **_kwargs: _FakeResponse(status_code=403, parsed=None),
    )
    monkeypatch.setattr(
        whoami,
        "get_worker_metrics",
        lambda **_kwargs: _FakeResponse(status_code=403, parsed=None),
    )

    state = _state()
    runner = CliRunner()
    result = runner.invoke(whoami.app, ["--json"], obj=state)

    assert result.exit_code == 0
    assert captured_keys == ["pk_env_override"]
    assert state.config.get_active_profile().poster_api_key is None


def test_key_resolvers_prefer_env_without_mutating_profile(monkeypatch) -> None:
    profile = Profile(name="default", poster_api_key="poster_saved", worker_api_key="worker_saved")

    monkeypatch.setenv("MULTIPL_POSTER_KEY", "poster_env")
    monkeypatch.setenv("MULTIPL_WORKER_KEY", "worker_env")

    assert resolve_poster_api_key(profile) == "poster_env"
    assert resolve_worker_api_key(profile) == "worker_env"
    assert profile.poster_api_key == "poster_saved"
    assert profile.worker_api_key == "worker_saved"
