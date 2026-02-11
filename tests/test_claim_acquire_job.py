from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import claim
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
    def __init__(self, calls: list[dict[str, Any]]):
        self.calls = calls

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
        return _FakeResponse(
            status_code=200,
            payload={
                "claim": {
                    "id": "claim_123",
                    "jobId": "job_123",
                    "workerId": "worker_1",
                    "status": "ACTIVE",
                    "leaseExpiresAt": "2026-02-11T00:05:00.000Z",
                    "createdAt": "2026-02-11T00:00:00.000Z",
                    "releasedAt": None,
                    "forfeitedAt": None,
                },
                "job": {
                    "id": "job_123",
                    "posterId": "poster_1",
                    "taskType": "custom.v1",
                    "input": {},
                    "acceptance": {},
                    "requestedModel": None,
                    "estimatedTokens": None,
                    "deadlineSeconds": None,
                    "payoutCents": 50,
                    "state": "CLAIMED",
                    "createdAt": "2026-02-11T00:00:00.000Z",
                    "updatedAt": "2026-02-11T00:00:00.000Z",
                    "availableAt": None,
                    "claimedAt": "2026-02-11T00:00:00.000Z",
                    "completedAt": None,
                    "expiresAt": "2026-02-11T01:00:00.000Z",
                    "moderationStatus": "pass",
                    "moderationModel": "omni-moderation-latest",
                    "moderationCategories": {},
                    "moderationScores": {},
                    "moderationAt": "2026-02-11T00:00:00.000Z",
                    "contentSha256": "content_sha",
                },
            },
        )


class _FakeClient:
    def __init__(self, http_client: _FakeHttpClient):
        self._http_client = http_client

    def get_httpx_client(self) -> _FakeHttpClient:
        return self._http_client


class _FakeClaimsCache:
    def __init__(self) -> None:
        self.claims: dict[tuple[str, str], str] = {}

    def set_claim(self, profile: str, job_id: str, claim_id: str) -> None:
        self.claims[(profile, job_id)] = claim_id

    def save(self) -> None:
        return


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={
            "default": Profile(
                name="default",
                worker_api_key="worker_test_key",
            )
        },
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_claim_acquire_by_job_calls_correct_endpoint(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    fake_client = _FakeClient(_FakeHttpClient(calls))
    fake_cache = _FakeClaimsCache()

    monkeypatch.setattr(claim, "ensure_client_available", lambda: None)
    monkeypatch.setattr(claim, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(claim.ClaimsCache, "load", lambda: fake_cache)

    runner = CliRunner()
    result = runner.invoke(
        claim.app,
        [
            "acquire",
            "--job",
            "job_123",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert "claim_123" in result.stdout
    assert "job_123" in result.stdout
    assert len(calls) == 1
    assert calls[0]["method"].lower() == "post"
    assert calls[0]["url"] == "/v1/claims/acquire"
    assert calls[0]["json"] == {"jobId": "job_123"}
    assert ("default", "job_123") in fake_cache.claims


def test_claim_acquire_rejects_task_type_and_job_combination(monkeypatch) -> None:
    monkeypatch.setattr(claim, "ensure_client_available", lambda: None)
    monkeypatch.setattr(claim, "build_client", lambda _base_url: _FakeClient(_FakeHttpClient([])))

    runner = CliRunner()
    result = runner.invoke(
        claim.app,
        [
            "acquire",
            "--task-type",
            "custom.v1",
            "--job",
            "job_123",
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "Provide exactly one of --task-type or --job." in result.stdout
