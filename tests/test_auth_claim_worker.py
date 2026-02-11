from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from multipl_cli._client.models.post_v1_workers_claim_response_200 import (
    PostV1WorkersClaimResponse200,
)
from multipl_cli._client.models.post_v1_workers_claim_response_200_worker import (
    PostV1WorkersClaimResponse200Worker,
)
from multipl_cli.app_state import AppState
from multipl_cli.commands import auth
from multipl_cli.config import Config, Profile


@dataclass
class _FakeResponse:
    status_code: int
    content: bytes
    headers: dict[str, str]
    parsed: object | None = None

    def json(self):
        raise ValueError("no json")


def _state(
    *,
    poster_key: str | None = "poster_test_key",
    claim_token: str | None = None,
    verification_code: str | None = None,
    claim_url: str | None = None,
) -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={
            "default": Profile(
                name="default",
                poster_api_key=poster_key,
                worker_claim_token=claim_token,
                worker_claim_verification_code=verification_code,
                worker_claim_url=claim_url,
            )
        },
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_auth_help_shows_claim_worker() -> None:
    runner = CliRunner()
    result = runner.invoke(auth.app, ["--help"], obj=_state())
    assert result.exit_code == 0
    assert "claim-worker" in result.stdout


def test_claim_worker_help() -> None:
    runner = CliRunner()
    result = runner.invoke(auth.app, ["claim-worker", "--help"], obj=_state())
    assert result.exit_code == 0
    assert "Claim a worker agent under the current poster profile" in result.stdout


def test_claim_worker_missing_poster_key_exits_2() -> None:
    runner = CliRunner()
    result = runner.invoke(auth.app, ["claim-worker", "token-123"], obj=_state(poster_key=None))
    assert result.exit_code == 2
    assert "Poster API key not configured" in result.stdout


def test_claim_worker_rate_limited_exits_4(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())

    def fake_claim_worker_api(**_kwargs):
        return _FakeResponse(
            status_code=429,
            content=b'{"error":"rate_limited"}',
            headers={"retry-after": "5"},
        )

    monkeypatch.setattr(auth, "claim_worker_api", fake_claim_worker_api)

    runner = CliRunner()
    result = runner.invoke(auth.app, ["claim-worker", "token-123"], obj=_state())
    assert result.exit_code == 4
    assert "Rate limited" in result.stdout


def test_claim_worker_missing_token_exits_1() -> None:
    runner = CliRunner()
    result = runner.invoke(auth.app, ["claim-worker"], obj=_state())
    assert result.exit_code == 1
    assert "No worker claim token found" in result.stdout


def test_claim_worker_success_json(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())
    monkeypatch.setattr(auth, "save_config", lambda _config: None)

    calls: list[dict] = []

    def fake_claim_worker_api(*, client, authorization, body):
        calls.append(
            {
                "client": client,
                "authorization": authorization,
                "claim_token": body.claim_token,
                "verification_code": body.verification_code,
            }
        )
        parsed = PostV1WorkersClaimResponse200(
            ok=True,
            worker=PostV1WorkersClaimResponse200Worker(
                id="worker_123",
                name="demo-worker",
                is_claimed=True,
                claimed_by_poster_id="poster_123",
            ),
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    monkeypatch.setattr(auth, "claim_worker_api", fake_claim_worker_api)

    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        [
            "claim-worker",
            "token-123",
            "--verification-code",
            "abc123",
            "--json",
        ],
        obj=_state(),
    )
    assert result.exit_code == 0
    assert "worker_123" in result.stdout
    assert len(calls) == 1
    assert calls[0]["authorization"] == "Bearer poster_test_key"
    assert calls[0]["claim_token"] == "token-123"
    assert calls[0]["verification_code"] == "abc123"


def test_claim_worker_uses_saved_claim_and_clears_after_success(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url: object())

    calls: list[dict] = []
    saved: list[Config] = []

    def fake_claim_worker_api(*, client, authorization, body):
        calls.append(
            {
                "client": client,
                "authorization": authorization,
                "claim_token": body.claim_token,
                "verification_code": body.verification_code,
            }
        )
        parsed = PostV1WorkersClaimResponse200(
            ok=True,
            worker=PostV1WorkersClaimResponse200Worker(
                id="worker_123",
                name="demo-worker",
                is_claimed=True,
                claimed_by_poster_id="poster_123",
            ),
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    def fake_save_config(config: Config):
        saved.append(config)

    monkeypatch.setattr(auth, "claim_worker_api", fake_claim_worker_api)
    monkeypatch.setattr(auth, "save_config", fake_save_config)

    state = _state(
        claim_token="saved-token-123",
        verification_code="saved-code-123",
        claim_url="https://example.com/claim",
    )
    runner = CliRunner()
    result = runner.invoke(auth.app, ["claim-worker"], obj=state)
    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["claim_token"] == "saved-token-123"
    assert calls[0]["verification_code"] == "saved-code-123"
    profile = state.config.get_active_profile()
    assert profile.worker_claim_token is None
    assert profile.worker_claim_verification_code is None
    assert profile.worker_claim_url is None
    assert len(saved) == 1
