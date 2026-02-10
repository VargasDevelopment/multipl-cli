from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from multipl_cli._client.models.post_v1_posters_wallet_bind_response_200 import (
    PostV1PostersWalletBindResponse200,
)
from multipl_cli._client.models.post_v1_posters_wallet_nonce_response_200 import (
    PostV1PostersWalletNonceResponse200,
)
from multipl_cli.app_state import AppState
from multipl_cli.commands import auth, poster_wallet
from multipl_cli.config import Config, Profile


@dataclass
class _FakeResponse:
    status_code: int
    content: bytes
    headers: dict[str, str]
    parsed: object | None = None


def _state(*, poster_key: str | None = "poster_test_key") -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={"default": Profile(name="default", poster_api_key=poster_key)},
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_auth_poster_wallet_help_shows_bind_and_nonce() -> None:
    runner = CliRunner()
    result = runner.invoke(auth.app, ["poster-wallet", "--help"], obj=_state())
    assert result.exit_code == 0
    assert "bind" in result.stdout
    assert "nonce" in result.stdout


def test_bind_requires_poster_key() -> None:
    runner = CliRunner()
    result = runner.invoke(poster_wallet.app, ["bind", "0x1234567890123456789012345678901234567890"], obj=_state(poster_key=None))
    assert result.exit_code == 2
    assert "Poster API key not configured" in result.stdout


def test_nonce_rate_limit_exits_4(monkeypatch) -> None:
    monkeypatch.setattr(poster_wallet, "ensure_client_available", lambda: None)
    monkeypatch.setattr(poster_wallet, "build_client", lambda _base_url: object())

    def fake_nonce(**_kwargs):
        return _FakeResponse(status_code=429, content=b'{"error":"rate_limited"}', headers={"retry-after": "7"})

    monkeypatch.setattr(poster_wallet, "get_poster_wallet_nonce", fake_nonce)

    runner = CliRunner()
    result = runner.invoke(
        poster_wallet.app,
        ["nonce", "0x1234567890123456789012345678901234567890"],
        obj=_state(),
    )
    assert result.exit_code == 4
    assert "Rate limited" in result.stdout


def test_bind_no_sign_exits_1_and_skips_bind(monkeypatch) -> None:
    monkeypatch.setattr(poster_wallet, "ensure_client_available", lambda: None)
    monkeypatch.setattr(poster_wallet, "build_client", lambda _base_url: object())

    def fake_nonce(**_kwargs):
        parsed = PostV1PostersWalletNonceResponse200(
            address="0x1234567890123456789012345678901234567890",
            nonce="nonce-123",
            message="Multipl poster wallet binding\n\nPoster ID: poster-1",
            expires_at="2026-02-10T00:00:00.000Z",
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    def fail_bind(**_kwargs):
        raise AssertionError("bind endpoint should not be called when --no-sign is used")

    monkeypatch.setattr(poster_wallet, "get_poster_wallet_nonce", fake_nonce)
    monkeypatch.setattr(poster_wallet, "bind_poster_wallet", fail_bind)

    runner = CliRunner()
    result = runner.invoke(
        poster_wallet.app,
        [
            "bind",
            "0x1234567890123456789012345678901234567890",
            "--no-sign",
        ],
        obj=_state(),
    )
    assert result.exit_code == 1
    assert "Signature step skipped" in result.stdout


def test_bind_missing_wallet_env_exits_1(monkeypatch) -> None:
    monkeypatch.delenv("MULTIPL_WALLET_PRIVATE_KEY", raising=False)
    monkeypatch.setattr(poster_wallet, "ensure_client_available", lambda: None)
    monkeypatch.setattr(poster_wallet, "build_client", lambda _base_url: object())

    def fake_nonce(**_kwargs):
        parsed = PostV1PostersWalletNonceResponse200(
            address="0x1234567890123456789012345678901234567890",
            nonce="nonce-123",
            message="Multipl poster wallet binding\n\nPoster ID: poster-1",
            expires_at="2026-02-10T00:00:00.000Z",
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    def fail_bind(**_kwargs):
        raise AssertionError("bind endpoint should not be called when env var is missing")

    monkeypatch.setattr(poster_wallet, "get_poster_wallet_nonce", fake_nonce)
    monkeypatch.setattr(poster_wallet, "bind_poster_wallet", fail_bind)

    runner = CliRunner()
    result = runner.invoke(
        poster_wallet.app,
        ["bind", "0x1234567890123456789012345678901234567890"],
        obj=_state(),
    )
    assert result.exit_code == 1
    assert "MULTIPL_WALLET_PRIVATE_KEY is required" in result.stdout


def test_bind_success(monkeypatch) -> None:
    monkeypatch.setattr(poster_wallet, "ensure_client_available", lambda: None)
    monkeypatch.setattr(poster_wallet, "build_client", lambda _base_url: object())
    monkeypatch.setenv(
        "MULTIPL_WALLET_PRIVATE_KEY",
        "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce036f4f9d9f04b922f2f2f",
    )

    calls: list[dict] = []

    def fake_nonce(**_kwargs):
        parsed = PostV1PostersWalletNonceResponse200(
            address="0x1234567890123456789012345678901234567890",
            nonce="nonce-123",
            message="Multipl poster wallet binding\n\nPoster ID: poster-1",
            expires_at="2026-02-10T00:00:00.000Z",
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    def fake_bind(*, client, authorization, body):
        calls.append(
            {
                "client": client,
                "authorization": authorization,
                "address": body.address,
                "nonce": body.nonce,
                "signature": body.signature,
            }
        )
        parsed = PostV1PostersWalletBindResponse200(
            wallet_address=body.address,
            wallet_bound_at="2026-02-10T00:01:00.000Z",
        )
        return _FakeResponse(status_code=200, content=b"{}", headers={}, parsed=parsed)

    monkeypatch.setattr(poster_wallet, "get_poster_wallet_nonce", fake_nonce)
    monkeypatch.setattr(poster_wallet, "bind_poster_wallet", fake_bind)

    runner = CliRunner()
    result = runner.invoke(
        poster_wallet.app,
        ["bind", "0x1234567890123456789012345678901234567890"],
        obj=_state(),
    )
    assert result.exit_code == 0
    assert "Poster wallet bound" in result.stdout
    assert len(calls) == 1
    assert calls[0]["authorization"] == "Bearer poster_test_key"
    assert calls[0]["address"] == "0x1234567890123456789012345678901234567890"
    assert calls[0]["nonce"] == "nonce-123"
    assert calls[0]["signature"].startswith("0x")
