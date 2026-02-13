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


def _template_fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "github_issue.v1.template.json"


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


def test_job_create_template_dry_run_uses_local_fixture(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template-file",
            str(_template_fixture_path()),
            "--set",
            "repo=octocat/hello-world",
            "--set",
            "issueNumber=42",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["taskType"] == "research.v1"
    assert payload["input"]["repo"] == "octocat/hello-world"
    assert payload["input"]["issueNumber"] == 42
    stages = payload["stages"]
    assert [stage["stageIndex"] for stage in stages] == [1, 2, 3]
    assert [stage["taskType"] for stage in stages] == ["research.v1", "extract.v1", "custom.v1"]
    assert [stage["payoutCents"] for stage in stages] == [1000, 2000, 2000]
    assert "octocat/hello-world" in stages[0]["input"]["prompt"]
    assert "42" in stages[0]["input"]["prompt"]
    assert "octocat/hello-world" in stages[1]["input"]["prompt"]
    assert "42" in stages[2]["input"]["prompt"]


def test_job_create_template_dry_run_set_boolean_coercion() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template-file",
            str(_template_fixture_path()),
            "--set",
            "repo=octocat/hello-world",
            "--set",
            "issueNumber=42",
            "--set",
            "prEnabled=true",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["input"]["prEnabled"] is True
    assert payload["stages"][0]["input"]["prEnabled"] is True


def test_job_create_template_set_integer_type_error_suggests_set_json() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template-file",
            str(_template_fixture_path()),
            "--set",
            "repo=octocat/hello-world",
            "--set",
            "issueNumber=abc",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
        ],
        obj=_state(),
    )

    assert result.exit_code == 2


def test_job_create_template_from_gh_populates_inputs() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template",
            "github_issue.v1",
            "--template-file",
            str(_template_fixture_path()),
            "--from-gh",
            "https://github.com/octocat/hello-world/issues/123?foo=bar",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["input"]["repo"] == "octocat/hello-world"
    assert payload["input"]["issueNumber"] == 123
    assert "octocat/hello-world" in payload["stages"][0]["input"]["prompt"]
    assert "123" in payload["stages"][0]["input"]["prompt"]


def test_job_create_template_from_gh_conflict_with_set_errors() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template",
            "github_issue.v1",
            "--template-file",
            str(_template_fixture_path()),
            "--from-gh",
            "https://github.com/octocat/hello-world/issues/123",
            "--set",
            "issueNumber=9",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
        ],
        obj=_state(),
    )

    assert result.exit_code == 2
    assert "--from-gh cannot be combined with --set/--set-json for:" in result.output
    assert "issueNumber" in result.output


def test_job_create_template_from_gh_requires_template_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template-file",
            str(_template_fixture_path()),
            "--from-gh",
            "https://github.com/octocat/hello-world/issues/123",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "--from-gh requires --template." in result.output


def test_job_create_template_payout_cents_guidance_for_multi_stage() -> None:
    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template-file",
            str(_template_fixture_path()),
            "--set",
            "repo=octocat/hello-world",
            "--set-json",
            "issueNumber=42",
            "--payout-cents",
            "5000",
            "--dry-run",
        ],
        obj=_state(),
    )

    assert result.exit_code == 1
    assert "Multi-stage jobs require explicit stage payouts." in result.stdout
    assert "You provided --payout-cents 5000." in result.stdout
    assert "--stage-payout-cents 1=1000" in result.stdout
    assert "--stage-payout-cents 2=2000" in result.stdout
    assert "3=2000" in result.stdout


def test_job_create_template_fetch_mock(monkeypatch) -> None:
    fixture_payload = json.loads(_template_fixture_path().read_text())
    parsed_template = job.GetV1TemplatesIdResponse200.from_dict(fixture_payload)

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url, api_key=None: object())

    def fake_get_template_by_id(*, id: str, client):
        assert id == "github_issue.v1"
        return _FakeDetailedResponse(status_code=200, parsed=parsed_template)

    monkeypatch.setattr(job, "get_template_by_id", fake_get_template_by_id)

    runner = CliRunner()
    result = runner.invoke(
        job.app,
        [
            "create",
            "--template",
            "github_issue.v1",
            "--set",
            "repo=octocat/hello-world",
            "--set-json",
            "issueNumber=8",
            "--stage-payout-cents",
            "1=1000",
            "--stage-payout-cents",
            "2=2000",
            "--stage-payout-cents",
            "3=2000",
            "--dry-run",
            "--json",
        ],
        obj=_state(),
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["stages"][0]["input"]["prompt"].startswith("Plan changes for octocat/hello-world")
