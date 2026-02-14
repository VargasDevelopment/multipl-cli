from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import auth
from multipl_cli.config import Config, Profile


@dataclass
class _FakeWallet:
    worker_id: str
    wallet_address: str
    network: str
    asset: str
    updated_at: str

    def to_dict(self):
        return {
            "workerId": self.worker_id,
            "walletAddress": self.wallet_address,
            "network": self.network,
            "asset": self.asset,
            "updatedAt": self.updated_at,
        }


@dataclass
class _FakeParsedResponse:
    wallet: _FakeWallet


@dataclass
class _FakeResponse:
    status_code: int
    parsed: _FakeParsedResponse | None = None


def _state(base_url: str) -> AppState:
    config = Config(
        base_url=base_url,
        active_profile="default",
        profiles={
            "default": Profile(
                name="default",
                worker_api_key="worker_test_key",
            )
        },
    )
    return AppState(config=config, profile_name="default", base_url=base_url)


def test_wallet_set_defaults_to_base_on_non_local_urls(monkeypatch) -> None:
    captured_networks: list[str] = []

    def fake_set_worker_wallet(*, client, body):
        captured_networks.append(str(body.network))
        return _FakeResponse(
            status_code=200,
            parsed=_FakeParsedResponse(
                wallet=_FakeWallet(
                    worker_id="worker_1",
                    wallet_address=body.address,
                    network=str(body.network),
                    asset="usdc",
                    updated_at="2026-02-11T00:00:00.000Z",
                )
            ),
        )

    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url, **_kwargs: object())
    monkeypatch.setattr(auth, "set_worker_wallet", fake_set_worker_wallet)

    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        ["wallet", "set", "0x1234567890123456789012345678901234567890", "--json"],
        obj=_state("https://multipl.dev/api"),
    )

    assert result.exit_code == 0
    assert captured_networks == ["eip155:8453"]


def test_wallet_set_defaults_to_local_for_localhost_urls(monkeypatch) -> None:
    captured_networks: list[str] = []

    def fake_set_worker_wallet(*, client, body):
        captured_networks.append(str(body.network))
        return _FakeResponse(
            status_code=200,
            parsed=_FakeParsedResponse(
                wallet=_FakeWallet(
                    worker_id="worker_1",
                    wallet_address=body.address,
                    network=str(body.network),
                    asset="usdc",
                    updated_at="2026-02-11T00:00:00.000Z",
                )
            ),
        )

    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url, **_kwargs: object())
    monkeypatch.setattr(auth, "set_worker_wallet", fake_set_worker_wallet)

    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        ["wallet", "set", "0x1234567890123456789012345678901234567890", "--json"],
        obj=_state("http://localhost:3001"),
    )

    assert result.exit_code == 0
    assert captured_networks == ["local"]


def test_wallet_set_network_override_takes_priority(monkeypatch) -> None:
    captured_networks: list[str] = []

    def fake_set_worker_wallet(*, client, body):
        captured_networks.append(str(body.network))
        return _FakeResponse(
            status_code=200,
            parsed=_FakeParsedResponse(
                wallet=_FakeWallet(
                    worker_id="worker_1",
                    wallet_address=body.address,
                    network=str(body.network),
                    asset="usdc",
                    updated_at="2026-02-11T00:00:00.000Z",
                )
            ),
        )

    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)
    monkeypatch.setattr(auth, "build_client", lambda _base_url, **_kwargs: object())
    monkeypatch.setattr(auth, "set_worker_wallet", fake_set_worker_wallet)

    runner = CliRunner()
    result = runner.invoke(
        auth.app,
        [
            "wallet",
            "set",
            "0x1234567890123456789012345678901234567890",
            "--network",
            "eip155:8453",
            "--json",
        ],
        obj=_state("http://localhost:3001"),
    )

    assert result.exit_code == 0
    assert captured_networks == ["eip155:8453"]
