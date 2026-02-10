from __future__ import annotations

from dataclasses import dataclass

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


def _register_response() -> _FakeResponse:
    parsed = PostV1WorkersRegisterResponse201(
        worker=PostV1WorkersRegisterResponse201Worker(
            id="worker_123",
            name="demo-worker",
            description=None,
            is_claimed=False,
        ),
        api_key="worker_api_key_123",
        claim_token="claim_token_123",
        claim_url="https://multipl.dev/claim?token=claim_token_123",
        verification_code="code_123",
    )
    return _FakeResponse(status_code=201, parsed=parsed)


def test_register_worker_persists_claim_artifacts(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "register_worker", lambda **_kwargs: _register_response())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)

    state = _state()
    runner = CliRunner()
    result = runner.invoke(auth.app, ["register", "worker"], obj=state)

    assert result.exit_code == 0
    profile = state.config.get_active_profile()
    assert profile.worker_api_key == "worker_api_key_123"
    assert profile.worker_claim_token == "claim_token_123"
    assert profile.worker_claim_verification_code == "code_123"
    assert profile.worker_claim_url == "https://multipl.dev/claim?token=claim_token_123"
    assert "claim_token_123" not in result.stdout
    assert "code_123" not in result.stdout


def test_register_worker_json_gates_claim_output(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "register_worker", lambda **_kwargs: _register_response())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)

    runner = CliRunner()

    result_without = runner.invoke(auth.app, ["register", "worker", "--json"], obj=_state())
    assert result_without.exit_code == 0
    assert "claim_token" not in result_without.stdout
    assert "verification_code" not in result_without.stdout

    result_with = runner.invoke(
        auth.app, ["register", "worker", "--json", "--show-claim"], obj=_state()
    )
    assert result_with.exit_code == 0
    assert "claim_token" in result_with.stdout
    assert "verification_code" in result_with.stdout


def test_login_worker_registration_persists_claim_artifacts(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "register_worker", lambda **_kwargs: _register_response())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)
    monkeypatch.setattr(auth, "_whoami_payload", lambda *_args, **_kwargs: {})

    state = _state()
    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        ["login", "--non-interactive", "--worker", "--no-poster"],
        obj=state,
    )

    assert result.exit_code == 0
    profile = state.config.get_active_profile()
    assert profile.worker_claim_token == "claim_token_123"
    assert profile.worker_claim_verification_code == "code_123"
    assert profile.worker_claim_url == "https://multipl.dev/claim?token=claim_token_123"
    assert "claim_token_123" not in result.stdout
