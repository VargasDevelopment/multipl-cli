from __future__ import annotations

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import job
from multipl_cli.config import Config, Profile


def _state() -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={"default": Profile(name="default", poster_api_key="poster_test_key")},
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


def test_job_help_lists_review_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(job.app, ["--help"], obj=_state())
    assert result.exit_code == 0
    assert "accept" in result.stdout
    assert "reject" in result.stdout


def test_job_accept_invokes_review_helper(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_review(state, *, job_id, decision, note, json_output):
        calls.append(
            {
                "state": state,
                "job_id": job_id,
                "decision": str(decision),
                "note": note,
                "json_output": json_output,
            }
        )

    monkeypatch.setattr(job, "_review_job", fake_review)

    runner = CliRunner()
    result = runner.invoke(
        job.app,
        ["accept", "job_123", "--note", "looks good", "--json"],
        obj=_state(),
    )
    assert result.exit_code == 0
    assert calls == [
        {
            "state": _state(),
            "job_id": "job_123",
            "decision": "accept",
            "note": "looks good",
            "json_output": True,
        }
    ]


def test_job_reject_invokes_review_helper(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_review(state, *, job_id, decision, note, json_output):
        calls.append(
            {
                "state": state,
                "job_id": job_id,
                "decision": str(decision),
                "note": note,
                "json_output": json_output,
            }
        )

    monkeypatch.setattr(job, "_review_job", fake_review)

    runner = CliRunner()
    result = runner.invoke(job.app, ["reject", "job_456"], obj=_state())
    assert result.exit_code == 0
    assert calls == [
        {
            "state": _state(),
            "job_id": "job_456",
            "decision": "reject",
            "note": None,
            "json_output": False,
        }
    ]
