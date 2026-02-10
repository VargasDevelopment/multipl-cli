from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from multipl_cli._client.models.get_v1_jobs_lane import GetV1JobsLane
from multipl_cli._client.models.get_v1_task_types_role import GetV1TaskTypesRole
from multipl_cli.app_state import AppState
from multipl_cli.commands import job, task
from multipl_cli.config import Config, Profile


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={"default": Profile(name="default")},
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_job_list_help_includes_lane_option() -> None:
    runner = CliRunner()
    result = runner.invoke(job.app, ["list", "--help"], obj=_state())
    assert result.exit_code == 0
    assert "--lane" in result.stdout


def test_task_group_help_includes_list() -> None:
    runner = CliRunner()
    result = runner.invoke(task.app, ["--help"], obj=_state())
    assert result.exit_code == 0
    assert "--role" in result.stdout


def test_task_list_rejects_invalid_role() -> None:
    runner = CliRunner()
    result = runner.invoke(task.app, ["--role", "invalid"], obj=_state())
    assert result.exit_code == 1
    assert "Invalid role" in result.stdout


@dataclass
class _FakeResponse:
    status_code: int
    content: bytes
    headers: dict[str, str]
    parsed: object | None = None


def test_job_list_lane_uses_lane_endpoint(monkeypatch) -> None:
    calls: list[dict] = []

    monkeypatch.setattr(job, "ensure_client_available", lambda: None)
    monkeypatch.setattr(job, "build_client", lambda _base_url: object())

    def fake_list_lane_jobs(*, client, lane, limit):
        calls.append({"client": client, "lane": lane, "limit": limit})
        return _FakeResponse(
            status_code=200,
            content=b'{"jobs":[],"nextCursor":null}',
            headers={},
        )

    def fail_public_jobs(**_kwargs):
        raise AssertionError("public endpoint should not be used when --lane is set")

    monkeypatch.setattr(job, "list_lane_jobs", fake_list_lane_jobs)
    monkeypatch.setattr(job, "list_public_jobs", fail_public_jobs)

    runner = CliRunner()
    result = runner.invoke(job.app, ["list", "--lane", "verifier", "--limit", "50"], obj=_state())
    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["lane"] == GetV1JobsLane.VERIFIER
    assert calls[0]["limit"] == 50


def test_task_list_role_uses_role_query_param(monkeypatch) -> None:
    calls: list[dict] = []

    monkeypatch.setattr(task, "ensure_client_available", lambda: None)
    monkeypatch.setattr(task, "build_client", lambda _base_url: object())

    def fake_get_task_types(*, client, role):
        calls.append({"client": client, "role": role})
        return _FakeResponse(
            status_code=200,
            content=b'[]',
            headers={},
        )

    monkeypatch.setattr(task, "get_task_types", fake_get_task_types)

    runner = CliRunner()
    result = runner.invoke(task.app, ["--role", "worker", "--json"], obj=_state())
    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["role"] == GetV1TaskTypesRole.WORKER
