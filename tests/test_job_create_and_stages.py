from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import job
from multipl_cli.config import Config, Profile


@dataclass
class _FakeHttpResponse:
    status_code: int
    payload: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)
    content: bytes = b""

    def __post_init__(self) -> None:
        if not self.content:
            self.content = json.dumps(self.payload).encode("utf-8")

    def json(self) -> dict[str, Any]:
        return self.payload


@dataclass
class _FakeDetailedResponse:
    status_code: int
    parsed: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    content: bytes = b"{}"


class _FakeHttpClient:
    def __init__(self, calls: list[dict[str, Any]], response: _FakeHttpResponse):
        self.calls = calls
        self.response = response

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> _FakeHttpResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": json,
            }
        )
        return self.response


class _FakeClient:
    def __init__(self, http_client: _FakeHttpClient):
        self._http_client = http_client

    def get_httpx_client(self) -> _FakeHttpClient:
        return self._http_client


@dataclass
class _ParsedPayload:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.payload


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={
            "default": Profile(
                name="default",
                poster_api_key="poster_test_key",
                worker_api_key="worker_test_key",
            )
        },
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.write_text(json.dumps(payload))
    return path


def test_job_create_legacy_wraps_input_payload(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    response = _FakeHttpResponse(
        status_code=201,
        payload={"job": {"id": "job_legacy", "state": "AVAILABLE"}},
    )
    fake_client = _FakeClient(_FakeHttpClient(calls, response))

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(job, "request_with_x402", lambda request_fn, **_kwargs: request_fn(None))

    input_file = _write_json(tmp_path / "legacy-input.json", {"prompt": "hello"})
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--task-type",
            "research.v1",
            "--input-file",
            str(input_file),
            "--idempotency-key",
            "idem-legacy",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    sent_payload = calls[0]["json"]
    assert sent_payload["taskType"] == "research.v1"
    assert sent_payload["input"] == {"prompt": "hello"}
    assert "stages" not in sent_payload


def test_job_create_detects_full_request_and_preserves_top_level_stages(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[dict[str, Any]] = []
    response = _FakeHttpResponse(
        status_code=201,
        payload={"job": {"id": "job_staged", "state": "AVAILABLE"}},
    )
    fake_client = _FakeClient(_FakeHttpClient(calls, response))

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(job, "request_with_x402", lambda request_fn, **_kwargs: request_fn(None))

    staged_request = {
        "taskType": "research.v1",
        "input": {"prompt": "root prompt"},
        "stages": [
            {"stageId": "plan", "name": "Plan", "taskType": "research.v1", "payoutCents": 50},
            {"stageId": "proof", "name": "Proof", "taskType": "research.v1", "payoutCents": 20},
        ],
    }
    input_file = _write_json(tmp_path / "staged-request.json", staged_request)
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--input-file",
            str(input_file),
            "--idempotency-key",
            "idem-staged",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    sent_payload = calls[0]["json"]
    assert sent_payload["taskType"] == "research.v1"
    assert "stages" in sent_payload
    assert sent_payload["stages"][0]["stageId"] == "plan"
    assert "stages" not in sent_payload["input"]


def test_job_create_request_file_mode_allows_task_type_override(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []
    response = _FakeHttpResponse(
        status_code=201,
        payload={"job": {"id": "job_override", "state": "AVAILABLE"}},
    )
    fake_client = _FakeClient(_FakeHttpClient(calls, response))

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: fake_client)
    monkeypatch.setattr(job, "request_with_x402", lambda request_fn, **_kwargs: request_fn(None))

    request_file = _write_json(
        tmp_path / "request-file.json",
        {"taskType": "old.v1", "input": {"prompt": "hello"}},
    )
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--request-file",
            "--task-type",
            "new.v1",
            "--input-file",
            str(request_file),
            "--idempotency-key",
            "idem-request-file",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["json"]["taskType"] == "new.v1"


def test_job_stages_calls_endpoint_and_renders_pipeline(monkeypatch) -> None:
    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: object())

    payload = {
        "rootJobId": "root-stage-job",
        "stages": [
            {"stageIndex": 1, "stageId": "plan", "state": "AVAILABLE", "visibility": "GATED"},
            {"stageIndex": 2, "stageId": "proof", "state": "LOCKED", "visibility": "PUBLIC"},
        ],
    }

    def fake_get_job_stages(*, client, job_id, authorization):
        assert job_id == "job_123"
        assert authorization == "Bearer poster_test_key"
        return _FakeDetailedResponse(status_code=200, parsed=_ParsedPayload(payload))

    monkeypatch.setattr(job, "get_job_stages", fake_get_job_stages)

    runner = CliRunner()
    result = runner.invoke(job.app, ["stages", "job_123"], obj=_state())

    assert result.exit_code == 0
    assert "root-stage-job" in result.stdout
    assert "plan" in result.stdout
    assert "proof" in result.stdout
