from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from typer.testing import CliRunner

from multipl_cli.app_state import AppState
from multipl_cli.commands import template
from multipl_cli.config import Config, Profile


def _state(*, poster_key: str | None = "poster_test_key") -> AppState:
    config = Config(
        base_url="https://multipl.dev/api",
        active_profile="default",
        profiles={
            "default": Profile(
                name="default",
                poster_api_key=poster_key,
            )
        },
    )
    return AppState(config=config, profile_name="default", base_url=config.base_url)


@dataclass
class _FakeResponse:
    status_code: int
    payload: Any
    headers: dict[str, str] | None = None
    parsed: Any = None

    @property
    def content(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_template_list_json_outputs_payload(monkeypatch) -> None:
    payload = [
        {
            "id": "github_issue.v1",
            "displayName": "GitHub Issue",
            "description": "desc",
            "version": "v1",
            "public": True,
            "stageCount": 3,
            "taskTypeIds": ["research.v1", "extract.v1", "custom.v1"],
            "capabilitySummary": {
                "requiresNetwork": True,
                "requiresGit": True,
                "allowsSideEffects": False,
            },
        },
        {
            "id": "research.v1.template.v1",
            "displayName": "Research",
            "description": "desc2",
            "version": "v1",
            "public": True,
            "stageCount": 1,
            "taskTypeIds": ["research.v1"],
            "capabilitySummary": {
                "requiresNetwork": False,
                "requiresGit": False,
                "allowsSideEffects": False,
            },
        },
    ]

    monkeypatch.setattr(template, "ensure_client_available", lambda: None)
    monkeypatch.setattr(template, "build_client", lambda _base_url, api_key=None: object())
    monkeypatch.setattr(
        template,
        "list_templates",
        lambda *, client: _FakeResponse(status_code=200, payload=payload, headers={}),
    )

    runner = CliRunner()
    result = runner.invoke(template.app, ["list", "--json"], obj=_state())
    assert result.exit_code == 0
    assert json.loads(result.stdout) == payload


def test_template_get_json_outputs_payload(monkeypatch) -> None:
    payload = {
        "id": "github_issue.v1",
        "displayName": "GitHub Issue",
        "description": "Template description",
        "version": "v1",
        "public": True,
        "stageCount": 3,
        "taskTypeIds": ["research.v1", "extract.v1", "custom.v1"],
        "capabilitySummary": {
            "requiresNetwork": True,
            "requiresGit": True,
            "allowsSideEffects": False,
        },
        "inputSchema": {
            "type": "object",
            "required": ["repo"],
            "properties": {"repo": {"type": "string"}},
        },
        "stages": [
            {
                "index": 1,
                "title": "Plan",
                "taskTypeId": "research.v1",
                "promptTemplate": "Prompt",
                "capabilities": {
                    "requiresNetwork": True,
                    "requiresGit": False,
                    "allowsSideEffects": False,
                },
            }
        ],
    }

    monkeypatch.setattr(template, "ensure_client_available", lambda: None)
    monkeypatch.setattr(template, "build_client", lambda _base_url, api_key=None: object())
    monkeypatch.setattr(
        template,
        "get_template_by_id",
        lambda id, *, client: _FakeResponse(status_code=200, payload=payload, headers={}),
    )

    runner = CliRunner()
    result = runner.invoke(template.app, ["get", "github_issue.v1", "--json"], obj=_state())
    assert result.exit_code == 0
    assert json.loads(result.stdout) == payload


def test_template_get_404_returns_user_friendly_error(monkeypatch) -> None:
    monkeypatch.setattr(template, "ensure_client_available", lambda: None)
    monkeypatch.setattr(template, "build_client", lambda _base_url, api_key=None: object())
    monkeypatch.setattr(
        template,
        "get_template_by_id",
        lambda id, *, client: _FakeResponse(
            status_code=404,
            payload={"error": "not_found"},
            headers={},
        ),
    )

    runner = CliRunner()
    result = runner.invoke(template.app, ["get", "missing.template.v1"], obj=_state())
    assert result.exit_code == 1
    assert "Template not found: missing.template.v1" in result.stdout
