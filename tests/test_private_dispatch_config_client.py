from __future__ import annotations

import json
import stat
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from multipl_cli import main
from multipl_cli.private_dispatch.client import PrivateClient
from multipl_cli.private_dispatch.config import DispatchConfigError, load_dispatch_config
from multipl_cli.private_dispatch.storage import Journal, atomic_write


def _write_config(tmp_path: Path, tasks: dict[str, object] | None = None) -> Path:
    path = tmp_path / "private.json"
    path.write_text(
        json.dumps(
            {
                "baseUrl": "https://private.multipl.test",
                "bearer": "secret-bearer",
                "scopeHeaders": {
                    "x-multipl-namespace": "tenant-a",
                    "x-multipl-lane": "agents",
                },
                "heartbeatSeconds": 5,
                "worktrees": tasks
                or {
                    "registry.id/document.index@1": {
                        "cwd": str(tmp_path),
                        "model": "gpt-5.6-codex",
                        "reasoning": "high",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    path.chmod(0o600)
    return path


def test_config_requires_credentials_secure_mode_and_exact_allowlist(tmp_path: Path) -> None:
    path = _write_config(tmp_path)
    config = load_dispatch_config(path)
    assert config.bearer == "secret-bearer"
    assert config.tasks[0].identity.key == "registry.id/document.index@1"
    assert config.tasks[0].cwd == tmp_path

    path.chmod(0o644)
    with pytest.raises(DispatchConfigError, match="0600"):
        load_dispatch_config(path)

    path = _write_config(tmp_path, {"document.index": {}})
    with pytest.raises(DispatchConfigError, match="exactly cwd"):
        load_dispatch_config(path)


def test_config_rejects_missing_credentials_and_nonpositive_version(tmp_path: Path) -> None:
    path = _write_config(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["bearer"] = ""
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(DispatchConfigError, match="bearer"):
        load_dispatch_config(path)

    path = _write_config(
        tmp_path,
        {
            "registry.id/document.index@0": {
                "cwd": str(tmp_path),
                "model": "gpt-5.6-codex",
                "reasoning": "high",
            }
        },
    )
    with pytest.raises(DispatchConfigError, match="positive-version"):
        load_dispatch_config(path)


def test_private_client_uses_scope_headers_exact_allowlist_and_accepts_204(tmp_path: Path) -> None:
    config = load_dispatch_config(_write_config(tmp_path))
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    with PrivateClient(config, httpx.MockTransport(handler)) as client:
        attempt = client.acquire(
            tuple(item.identity for item in config.tasks),
            "stable-acquire-key",
        )

    assert attempt is None
    assert len(requests) == 1
    request = requests[0]
    assert request.url.path == "/private/v1/attempts/acquire-next"
    assert request.headers["authorization"] == "Bearer secret-bearer"
    assert request.headers["x-multipl-namespace"] == "tenant-a"
    assert request.headers["x-multipl-lane"] == "agents"
    assert request.headers["idempotency-key"] == "stable-acquire-key"
    assert json.loads(request.content) == {
        "taskAllowlist": [
            {"registryId": "registry.id", "typeId": "document.index", "version": 1}
        ]
    }


def test_private_client_parses_authoritative_registry_work_and_renew_shapes(tmp_path: Path) -> None:
    config = load_dispatch_config(_write_config(tmp_path))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("task-registry"):
            return httpx.Response(
                200,
                json={
                    "registryId": "registry.id",
                    "revision": 1,
                    "tasks": [
                        {
                            "typeId": "document.index",
                            "version": 1,
                            "resultSchema": {"type": "object"},
                        }
                    ],
                },
            )
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "workId": "work-1",
                    "task": {
                        "registryId": "registry.id",
                        "typeId": "document.index",
                        "version": 1,
                    },
                    "input": {"document": "hello"},
                },
            )
        return httpx.Response(
            200,
            json={
                "attempt": {
                    "id": "attempt-1",
                    "workId": "work-1",
                    "lease": {
                        "leaseId": "00000000-0000-4000-8000-000000000001",
                        "generation": 2,
                        "expiresAt": "2030-01-01T00:00:00.000Z",
                    },
                }
            },
        )

    with PrivateClient(config, httpx.MockTransport(handler)) as client:
        contract = client.task_contracts()[0]
        work = client.work("work-1")
        from multipl_cli.private_dispatch.types import Attempt, Lease

        renewed = client.renew(
            Attempt(
                "attempt-1",
                "work-1",
                Lease("00000000-0000-4000-8000-000000000001", 1, "soon"),
            ),
            "renew-key",
        )
    assert contract.identity == work.task
    assert work.input == {"document": "hello"}
    assert renewed.lease.generation == 2


def test_atomic_storage_enforces_secret_modes(tmp_path: Path) -> None:
    state = tmp_path / "state"
    path = state / "payload.json"
    atomic_write(path, b"secret")
    assert stat.S_IMODE(state.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600

    journal = Journal(state)
    journal.write({"state": "claimed"})
    assert journal.load() == {"state": "claimed"}
    assert stat.S_IMODE(journal.path.stat().st_mode) == 0o600


def test_private_command_does_not_load_public_cli_config(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        main,
        "load_config",
        lambda: (_ for _ in ()).throw(AssertionError("public config must not load")),
    )
    result = CliRunner().invoke(
        main.app,
        ["private", "dispatch-once", "--config", str(tmp_path / "missing.json")],
    )
    assert result.exit_code == 2
    assert "does not exist" in result.stdout
