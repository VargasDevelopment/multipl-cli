from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import submit
from multipl_cli.config import Config, Profile


@dataclass
class _FakeResponse:
    status_code: int
    payload: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)
    content: bytes = b""

    def __post_init__(self) -> None:
        if not self.content:
            self.content = json.dumps(self.payload).encode("utf-8")

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
        if method.lower() == "get" and url == "/v1/public/jobs/job_stage_1":
            return _FakeResponse(
                status_code=200,
                payload={
                    "job": {
                        "id": "job_stage_1",
                        "taskType": "research.v1",
                        "state": "AVAILABLE",
                        "payoutCents": 50,
                        "requestedModel": None,
                        "estimatedTokens": None,
                        "deadlineSeconds": None,
                        "createdAt": "2026-02-11T00:00:00.000Z",
                        "claimedAt": None,
                        "submittedAt": None,
                        "completedAt": None,
                        "isPlatformPosted": True,
                        "seedBatch": None,
                        "inputPreview": None,
                        "acceptancePreview": None,
                        "acceptanceContract": {
                            "outputSchema": {
                                "type": "object",
                                "required": ["copy"],
                                "properties": {
                                    "copy": {"type": "string"},
                                },
                            }
                        },
                        "availableAt": "2026-02-11T00:00:00.000Z",
                    },
                    "submissionSummary": None,
                    "results": {
                        "isSubmitted": False,
                        "isUnlocked": False,
                        "artifactExpiresAt": None,
                    },
                    "stages": [
                        {
                            "stageId": "stage_1",
                            "stageIndex": 1,
                            "name": "Stage 1",
                            "taskType": "research.v1",
                            "visibility": "GATED",
                            "state": "AVAILABLE",
                            "payoutCents": 50,
                            "isUnlocked": False,
                        }
                    ],
                },
            )

        if method.lower() == "post" and url == "/v1/claims/claim_1/submit":
            output = (json or {}).get("output", {})
            if isinstance(output, dict) and "copy" in output:
                acceptance_report = {
                    "version": "acceptance.v1",
                    "status": "pass",
                    "checks": [{"name": "schema", "passed": True, "reason": None}],
                    "stats": {"bytes": 16},
                    "commitment": {"sha256": "abc", "computedAt": "2026-02-11T00:00:00.000Z"},
                }
            else:
                acceptance_report = {
                    "version": "acceptance.v1",
                    "status": "fail",
                    "checks": [
                        {
                            "name": "schema",
                            "passed": False,
                            "reason": "output does not match schema",
                        }
                    ],
                    "stats": {"bytes": 16},
                    "commitment": {"sha256": "abc", "computedAt": "2026-02-11T00:00:00.000Z"},
                }
            return _FakeResponse(
                status_code=200,
                payload={
                    "submission": {
                        "id": "submission_1",
                        "jobId": "job_stage_1",
                        "claimId": "claim_1",
                        "workerId": "worker_1",
                        "output": output,
                        "moderationStatus": "pass",
                        "moderationModel": "omni-moderation-latest",
                        "moderationCategories": {},
                        "moderationScores": {},
                        "moderationAt": "2026-02-11T00:00:00.000Z",
                        "contentSha256": "content_sha",
                        "quarantineReason": None,
                        "stagePolicyViolations": None,
                        "stagePolicyViolationCount": 0,
                        "modelUsed": None,
                        "tokensUsed": None,
                        "createdAt": "2026-02-11T00:00:00.000Z",
                    },
                    "job": {
                        "id": "job_stage_1",
                        "posterId": "poster_1",
                        "taskType": "research.v1",
                        "input": {},
                        "acceptance": {},
                        "requestedModel": None,
                        "estimatedTokens": None,
                        "deadlineSeconds": None,
                        "payoutCents": 50,
                        "state": "SUBMITTED",
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
                    "acceptanceReport": acceptance_report,
                },
            )

        return _FakeResponse(status_code=404, payload={"error": "not_found"})


class _FakeClient:
    def __init__(self, http_client: _FakeHttpClient):
        self._http_client = http_client

    def get_httpx_client(self) -> _FakeHttpClient:
        return self._http_client


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


def _setup_client(monkeypatch, calls: list[dict[str, Any]]) -> None:
    fake_client = _FakeClient(_FakeHttpClient(calls))
    monkeypatch.setattr(submit, "ensure_client_available", lambda: None)
    monkeypatch.setattr(submit, "build_client", lambda _base_url: fake_client)


def test_submit_validate_staged_payload_fails_schema(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    _setup_client(monkeypatch, calls)

    payload_file = tmp_path / "invalid.json"
    payload_file.write_text(json.dumps({"wrong": "shape"}))

    runner = CliRunner()
    result = runner.invoke(
        submit.app,
        [
            "validate",
            "--job",
            "job_stage_1",
            "--file",
            str(payload_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "Acceptance Report (fail)" in result.stdout
    assert "schema" in result.stdout


def test_submit_validate_staged_payload_passes(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    _setup_client(monkeypatch, calls)

    payload_file = tmp_path / "valid.json"
    payload_file.write_text(json.dumps({"copy": "hello"}))

    runner = CliRunner()
    result = runner.invoke(
        submit.app,
        [
            "validate",
            "--job",
            "job_stage_1",
            "--file",
            str(payload_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert "Acceptance Report (pass)" in result.stdout


def test_submit_send_failed_acceptance_is_loud_and_nonzero(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    _setup_client(monkeypatch, calls)

    payload_file = tmp_path / "invalid-send.json"
    payload_file.write_text(json.dumps({"wrong": "shape"}))

    runner = CliRunner()
    result = runner.invoke(
        submit.app,
        [
            "send",
            "--job",
            "job_stage_1",
            "--claim",
            "claim_1",
            "--force",
            "--file",
            str(payload_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "FAILED ACCEPTANCE" in result.stdout
    assert "Submission accepted (PASS)." not in result.stdout
    post_calls = [call for call in calls if call["method"].lower() == "post"]
    assert len(post_calls) == 1
    assert post_calls[0]["json"]["expectedJobId"] == "job_stage_1"


def test_submit_send_valid_payload_prints_success(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    _setup_client(monkeypatch, calls)

    payload_file = tmp_path / "valid-send.json"
    payload_file.write_text(json.dumps({"copy": "hello"}))

    runner = CliRunner()
    result = runner.invoke(
        submit.app,
        [
            "send",
            "--job",
            "job_stage_1",
            "--claim",
            "claim_1",
            "--file",
            str(payload_file),
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert "Submission accepted (PASS)." in result.stdout
