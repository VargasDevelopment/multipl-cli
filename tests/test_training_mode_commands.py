from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import auth, claim, job, submit
from multipl_cli.config import Config, Profile


@dataclass
class _FakeResponse:
    status_code: int
    payload: dict[str, Any]
    headers: dict[str, str] | None = None
    content: bytes = b""

    def json(self) -> dict[str, Any]:
        return self.payload


class _FakeHttpClient:
    def __init__(self, calls: list[dict[str, Any]], responses: dict[str, _FakeResponse]):
        self.calls = calls
        self.responses = responses

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> _FakeResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": json,
            }
        )
        return self.responses[url]


class _FakeClient:
    def __init__(self, http_client: _FakeHttpClient):
        self._http_client = http_client

    def get_httpx_client(self) -> _FakeHttpClient:
        return self._http_client


class _FakeClaimsCache:
    def __init__(self) -> None:
        self.claims_by_profile: dict[str, dict[str, str]] = {}
        self.saved = False

    def get_claim(self, profile: str, job_id: str) -> str | None:
        return self.claims_by_profile.get(profile, {}).get(job_id)

    def set_claim(self, profile: str, job_id: str, claim_id: str) -> None:
        self.claims_by_profile.setdefault(profile, {})[job_id] = claim_id

    def save(self) -> None:
        self.saved = True


def _state() -> AppState:
    config = Config(
        base_url="https://train.multipl.dev/api",
        active_profile="training",
        profiles={"training": Profile(name="training", base_url="https://train.multipl.dev/api")},
    )
    return AppState(
        config=config,
        profile_name="training",
        base_url=config.base_url,
        training_mode=True,
    )


def test_job_create_uses_training_validate_endpoint(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    fake_client = _FakeClient(
        _FakeHttpClient(
            calls,
            {
                "/v1/training/validate-job": _FakeResponse(
                    status_code=200,
                    payload={"mode": "training", "pass": True, "diagnostics": []},
                )
            },
        )
    )

    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps({"prompt": "hello"}))

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: fake_client)

    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--task-type",
            "classify.v1",
            "--input-file",
            str(input_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["url"] == "/v1/training/validate-job"
    assert calls[0]["headers"] == {"Content-Type": "application/json"}
    assert calls[0]["json"]["taskType"] == "classify.v1"


def test_job_create_template_in_training_uses_training_template_endpoint(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    fake_client = _FakeClient(
        _FakeHttpClient(
            calls,
            {
                "/v1/training/templates/classify.v1.template.v1": _FakeResponse(
                    status_code=200,
                    payload={
                        "id": "classify.v1.template.v1",
                        "displayName": "Classify Ticket",
                        "description": "Classify support ticket urgency.",
                        "version": "1.0.0",
                        "public": True,
                        "stageCount": 1,
                        "taskTypeIds": ["classify.v1"],
                        "capabilitySummary": {
                            "requiresNetwork": False,
                            "requiresGit": False,
                            "allowsSideEffects": False,
                        },
                        "inputSchema": {
                            "type": "object",
                            "properties": {"ticket": {"type": "string"}},
                            "required": ["ticket"],
                        },
                        "stages": [
                            {
                                "index": 1,
                                "title": "Classify",
                                "taskTypeId": "classify.v1",
                                "promptTemplate": "Label this ticket: {{ticket}}",
                                "capabilities": {
                                    "requiresNetwork": False,
                                    "requiresGit": False,
                                    "allowsSideEffects": False,
                                },
                            }
                        ],
                    },
                ),
                "/v1/training/validate-job": _FakeResponse(
                    status_code=200,
                    payload={"mode": "training", "pass": True, "diagnostics": []},
                ),
            },
        )
    )

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: fake_client)

    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template",
            "classify.v1.template.v1",
            "--set",
            "ticket=payment page is down",
            "--payout-cents",
            "25",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 2
    assert calls[0]["url"] == "/v1/training/templates/classify.v1.template.v1"
    assert calls[1]["url"] == "/v1/training/validate-job"
    assert calls[1]["json"]["taskType"] == "classify.v1"


def test_claim_acquire_uses_training_lease_without_worker_key(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    fake_client = _FakeClient(
        _FakeHttpClient(
            calls,
            {
                "/v1/training/lease": _FakeResponse(
                    status_code=200,
                    payload={
                        "mode": "training",
                        "lease": {
                            "leaseId": "lease_1",
                            "submitToken": "token_1",
                            "exerciseId": "cls-001",
                            "taskType": "classify.v1",
                            "issuedAt": "2026-02-14T00:00:00.000Z",
                            "expiresAt": "2026-02-14T00:05:00.000Z",
                            "ttlSeconds": 300,
                        },
                        "exercise": {
                            "id": "cls-001",
                            "title": "Simple label classification",
                            "taskType": "classify.v1",
                            "prompt": "Return label.",
                            "input": {"ticket": "x"},
                            "acceptanceContract": {},
                        },
                    },
                )
            },
        )
    )
    fake_cache = _FakeClaimsCache()

    monkeypatch.setattr(claim, "ensure_client_available", lambda: None)
    monkeypatch.setattr(claim, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(claim.ClaimsCache, "load", lambda: fake_cache)

    runner = CliRunner()
    result = runner.invoke(
        claim.app,
        ["acquire", "--task-type", "classify.v1"],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["url"] == "/v1/training/lease"
    assert calls[0]["json"] == {"taskType": "classify.v1"}
    assert "exercise.title" in result.stdout
    assert "Simple label classification" in result.stdout
    assert "prompt" in result.stdout
    assert "input" in result.stdout
    assert '{"ticket":"x"}' in result.stdout
    assert fake_cache.saved is True
    assert fake_cache.get_claim("training", "cls-001") == "lease_1:token_1"


def test_submit_send_uses_training_submit_endpoint(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    fake_client = _FakeClient(
        _FakeHttpClient(
            calls,
            {
                "/v1/training/submit": _FakeResponse(
                    status_code=200,
                    payload={
                        "mode": "training",
                        "leaseId": "lease_1",
                        "exerciseId": "cls-001",
                        "pass": True,
                        "acceptanceReport": {
                            "version": "acceptance.v1",
                            "status": "pass",
                            "checks": [],
                            "stats": {"bytes": 20},
                            "commitment": {
                                "sha256": "abc",
                                "computedAt": "2026-02-14T00:00:00.000Z",
                            },
                        },
                        "diagnostics": [],
                    },
                )
            },
        )
    )
    fake_cache = _FakeClaimsCache()
    fake_cache.set_claim("training", "cls-001", "lease_1:token_1")

    payload_file = tmp_path / "output.json"
    payload_file.write_text(json.dumps({"label": "low"}))

    monkeypatch.setattr(submit, "ensure_client_available", lambda: None)
    monkeypatch.setattr(submit, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(submit.ClaimsCache, "load", lambda: fake_cache)

    runner = CliRunner()
    result = runner.invoke(
        submit.app,
        [
            "send",
            "--job",
            "cls-001",
            "--file",
            str(payload_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["url"] == "/v1/training/submit"
    assert calls[0]["json"]["leaseId"] == "lease_1"
    assert calls[0]["json"]["submitToken"] == "token_1"
    assert calls[0]["json"]["output"] == {"label": "low"}


def test_wallet_commands_disabled_in_training(monkeypatch) -> None:
    monkeypatch.setattr(auth, "ensure_client_available", lambda: None)

    runner = CliRunner()
    result = runner.invoke(
        auth.wallet_app,
        [
            "0x1234567890123456789012345678901234567890",
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "disabled in training mode" in result.stdout


def test_job_get_fails_gracefully_in_training(monkeypatch) -> None:
    monkeypatch.setattr(job, "ensure_client_available", lambda: None)

    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "get",
            "ver-002",
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "unavailable in training mode" in result.stdout
