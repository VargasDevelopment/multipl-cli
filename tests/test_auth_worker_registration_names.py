from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from typer.testing import CliRunner

from multipl_cli._client.models.post_v1_workers_register_response_201 import (
    PostV1WorkersRegisterResponse201,
)
from multipl_cli._client.models.post_v1_workers_register_response_201_worker import (
    PostV1WorkersRegisterResponse201Worker,
)
from multipl_cli.app_state import AppState
from multipl_cli.commands import auth
from multipl_cli.config import Config, Profile


@dataclass
class _FakeResponse:
    status_code: int
    parsed: object | None = None


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={"default": Profile(name="default")},
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def _register_response(*, worker_name: str) -> _FakeResponse:
    parsed = PostV1WorkersRegisterResponse201(
        worker=PostV1WorkersRegisterResponse201Worker(
            id="worker_123",
            name=worker_name,
            description=None,
            is_claimed=False,
        ),
        api_key="worker_api_key_123",
        claim_token="claim_token_123",
        claim_url="https://multipl.dev/claim?token=claim_token_123",
        verification_code="code_123",
    )
    return _FakeResponse(status_code=201, parsed=parsed)


def test_generate_default_worker_name_is_stable_for_state_dir() -> None:
    first = auth.generate_default_worker_name("default", Path("/tmp/multipl/worker-a"))
    second = auth.generate_default_worker_name("default", Path("/tmp/multipl/worker-a"))
    third = auth.generate_default_worker_name("default", Path("/tmp/multipl/worker-b"))

    assert first == second
    assert first != third
    assert first.startswith("default-worker-")


def test_register_worker_retries_on_409_for_auto_name(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)
    monkeypatch.setattr(auth, "get_state_dir", lambda: Path("/tmp/multipl/agent-01"))

    attempted_names: list[str] = []
    responses = [_FakeResponse(status_code=409), _register_response(worker_name="retry-success")]

    def fake_register_worker(*, client, body):
        attempted_names.append(body.name)
        return responses.pop(0)

    monkeypatch.setattr(auth, "register_worker", fake_register_worker)

    runner = CliRunner()
    result = runner.invoke(auth.app, ["register", "worker", "--json"], obj=_state())

    assert result.exit_code == 0
    base = auth.generate_default_worker_name("default", Path("/tmp/multipl/agent-01"))
    assert attempted_names == [base, f"{base}-2"]


def test_register_worker_with_explicit_name_fails_cleanly_on_409(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)

    attempted_names: list[str] = []

    def fake_register_worker(*, client, body):
        attempted_names.append(body.name)
        return _FakeResponse(status_code=409)

    monkeypatch.setattr(auth, "register_worker", fake_register_worker)

    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        ["register", "worker", "--name", "my-worker"],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert attempted_names == ["my-worker"]
    assert "already exists" in result.stdout
