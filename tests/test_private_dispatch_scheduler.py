from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from multipl_cli.private_dispatch.agent import AgentOutcome, AgentRunner, child_environment
from multipl_cli.private_dispatch.client import PrivateApiError
from multipl_cli.private_dispatch.scheduler import Dispatcher
from multipl_cli.private_dispatch.storage import Journal, acquire_lock
from multipl_cli.private_dispatch.types import (
    Attempt,
    DispatchConfig,
    Lease,
    TaskContract,
    TaskIdentity,
    TaskPolicy,
    Work,
)

IDENTITY = TaskIdentity("registry.id", "document.index", 1)
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "required": ["result"],
    "properties": {"result": {"type": "string"}},
}


def _config(tmp_path: Path, heartbeat: float = 1) -> DispatchConfig:
    return DispatchConfig(
        base_url="https://private.multipl.test",
        bearer="secret-bearer",
        namespace="tenant-a",
        lane="agents",
        tasks=(TaskPolicy(IDENTITY, "gpt-5.6-codex", "high", tmp_path),),
        state_dir=tmp_path / "state",
        heartbeat_seconds=heartbeat,
    )


def _attempt(generation: int = 1) -> Attempt:
    return Attempt(
        "attempt-1",
        "work-1",
        Lease("00000000-0000-4000-8000-000000000001", generation, "2030-01-01T00:00:00Z"),
    )


class FakeClient:
    def __init__(self, attempt: Attempt | None = None, submit_failures: int = 0) -> None:
        self.next_attempt = attempt
        self.submit_failures = submit_failures
        self.acquires: list[tuple[tuple[TaskIdentity, ...], str]] = []
        self.submissions: list[tuple[Attempt, object, str]] = []
        self.renews: list[str] = []

    def task_contracts(self) -> tuple[TaskContract, ...]:
        return (TaskContract(IDENTITY, SCHEMA),)

    def acquire(self, allowlist: tuple[TaskIdentity, ...], key: str) -> Attempt | None:
        self.acquires.append((allowlist, key))
        value = self.next_attempt
        self.next_attempt = None
        return value

    def work(self, work_id: str) -> Work:
        assert work_id == "work-1"
        return Work(work_id, IDENTITY, {"document": "hello"})

    def renew(self, attempt: Attempt, key: str) -> Attempt:
        self.renews.append(key)
        return _attempt(attempt.lease.generation + 1)

    def submit(self, attempt: Attempt, payload: object, key: str) -> None:
        self.submissions.append((attempt, payload, key))
        if self.submit_failures:
            self.submit_failures -= 1
            raise PrivateApiError("submit result", 503)


class FakeRunner:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, attempt, work, policy, result_schema, renew) -> AgentOutcome:
        self.calls += 1
        assert work.task == IDENTITY
        assert policy.cwd.is_absolute()
        assert result_schema == SCHEMA
        return AgentOutcome(attempt, {"result": "done"}, "success")


def test_empty_queue_exits_before_prompt_or_launch(tmp_path: Path) -> None:
    client = FakeClient()
    runner = FakeRunner()
    result = Dispatcher(_config(tmp_path), client, runner).dispatch_once()
    assert result.code == 0
    assert result.message == "No private work available."
    assert len(client.acquires) == 1
    assert client.acquires[0][0] == (IDENTITY,)
    assert runner.calls == 0
    assert client.submissions == []


def test_process_lock_overlap_is_success_and_does_not_acquire(tmp_path: Path) -> None:
    config = _config(tmp_path)
    client = FakeClient(_attempt())
    with acquire_lock(config.state_dir):
        result = Dispatcher(config, client, FakeRunner()).dispatch_once()
    assert result.code == 0
    assert client.acquires == []


def test_registry_mismatch_fails_closed_without_task_fallback(tmp_path: Path) -> None:
    client = FakeClient(_attempt())
    client.task_contracts = lambda: (
        TaskContract(TaskIdentity("registry.id", "document.index", 2), SCHEMA),
    )
    runner = FakeRunner()
    result = Dispatcher(_config(tmp_path), client, runner).dispatch_once()
    assert result.code == 2
    assert client.acquires == []
    assert runner.calls == 0


def test_one_acquire_one_launch_and_successful_result(tmp_path: Path) -> None:
    client = FakeClient(_attempt())
    runner = FakeRunner()
    result = Dispatcher(_config(tmp_path), client, runner).dispatch_once()
    assert result.code == 0
    assert len(client.acquires) == 1
    assert runner.calls == 1
    assert len(client.submissions) == 1
    assert client.submissions[0][1] == {"result": "done"}
    assert not Journal(_config(tmp_path).state_dir).path.exists()


def test_submit_failure_retries_without_relaunch_before_next_acquire(tmp_path: Path) -> None:
    config = _config(tmp_path)
    first_client = FakeClient(_attempt(), submit_failures=1)
    first_runner = FakeRunner()
    first = Dispatcher(config, first_client, first_runner).dispatch_once()
    assert first.code == 2
    assert first_runner.calls == 1
    pending_key = first_client.submissions[0][2]

    second_client = FakeClient()
    second_runner = FakeRunner()
    second = Dispatcher(config, second_client, second_runner).dispatch_once()
    assert second.code == 0
    assert second_runner.calls == 0
    assert len(second_client.submissions) == 1
    assert second_client.submissions[0][2] == pending_key
    assert len(second_client.acquires) == 1


def test_restart_after_launch_submits_unknown_and_never_relaunches(tmp_path: Path) -> None:
    config = _config(tmp_path)
    journal = Journal(config.state_dir)
    journal.write(
        {
            "state": "launched",
            "attempt": {
                "attemptId": "attempt-1",
                "workId": "work-1",
                "lease": {
                    "leaseId": _attempt().lease.lease_id,
                    "generation": 1,
                    "expiresAt": _attempt().lease.expires_at,
                },
            },
            "taskKey": IDENTITY.key,
        }
    )
    client = FakeClient()
    runner = FakeRunner()
    result = Dispatcher(config, client, runner).dispatch_once()
    assert result.code == 0
    assert runner.calls == 0
    assert client.submissions[0][1] == {
        "dispatcher": {
            "status": "failure",
            "code": "restart_after_launch",
            "retryAgent": False,
        }
    }


def test_restart_after_claim_records_failure_without_launch(tmp_path: Path) -> None:
    config = _config(tmp_path)
    Journal(config.state_dir).write(
        {
            "state": "claimed",
            "attempt": {
                "attemptId": "attempt-1",
                "workId": "work-1",
                "lease": {
                    "leaseId": _attempt().lease.lease_id,
                    "generation": 1,
                    "expiresAt": _attempt().lease.expires_at,
                },
            },
        }
    )
    client = FakeClient()
    runner = FakeRunner()
    result = Dispatcher(config, client, runner).dispatch_once()
    assert result.code == 0
    assert runner.calls == 0
    assert client.submissions[0][1] == {
        "dispatcher": {
            "status": "failure",
            "code": "restart_after_claim",
            "retryAgent": False,
        }
    }


def _fake_codex(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "codex"
    executable.write_text("#!/usr/bin/python3\n" + body, encoding="utf-8")
    executable.chmod(0o700)
    return executable


def test_agent_exact_argv_env_stdin_schema_and_output(monkeypatch, tmp_path: Path) -> None:
    _fake_codex(
        tmp_path,
        """import json, os, sys
args = sys.argv[1:]
output = args[args.index('--output-last-message') + 1]
capture = {
    'args': args,
    'cwd': os.getcwd(),
    'env': dict(os.environ),
    'stdin': sys.stdin.read(),
    'schema': json.load(open(args[args.index('--output-schema') + 1])),
}
json.dump(capture, open('capture.json', 'w'))
json.dump({'result': 'done'}, open(output, 'w'))
""",
    )
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    monkeypatch.setenv("MULTIPL_BEARER", "must-not-leak")
    monkeypatch.setenv("MULTIPL_PRIVATE_CONFIG", "/secret/config")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-leak")
    runner = AgentRunner(tmp_path / "state", 5)
    outcome = runner.run(
        _attempt(),
        Work("work-1", IDENTITY, {"document": "hello"}),
        _config(tmp_path).tasks[0],
        SCHEMA,
        lambda attempt: attempt,
    )
    capture = json.loads((tmp_path / "capture.json").read_text(encoding="utf-8"))
    schema_path = tmp_path / "state" / "artifacts" / "output-schema.json"
    output_path = tmp_path / "state" / "artifacts" / "output-last-message.json"
    assert capture["args"] == [
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "-C",
        str(tmp_path),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(output_path),
        "--model",
        "gpt-5.6-codex",
        "--config",
        'model_reasoning_effort="high"',
        "-",
    ]
    assert capture["cwd"] == str(tmp_path)
    assert capture["schema"] == SCHEMA
    assert '"document":"hello"' in capture["stdin"]
    assert '"registryId":"registry.id"' in capture["stdin"]
    assert all(not key.startswith("MULTIPL_") for key in capture["env"])
    assert "UNRELATED_SECRET" not in capture["env"]
    assert outcome.payload == {"result": "done"}
    assert stat.S_IMODE(schema_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o600


def test_lease_loss_terminates_agent_process_group(monkeypatch, tmp_path: Path) -> None:
    _fake_codex(
        tmp_path,
        """import os, signal, time
def stop(_signal, _frame):
    open('terminated', 'w').write('yes')
    raise SystemExit(42)
signal.signal(signal.SIGTERM, stop)
time.sleep(10)
""",
    )
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    runner = AgentRunner(tmp_path / "state", 0.25)

    renewals = 0

    def lose_lease(_attempt: Attempt) -> Attempt:
        nonlocal renewals
        renewals += 1
        raise PrivateApiError("renew", 404)

    outcome = runner.run(
        _attempt(),
        Work("work-1", IDENTITY, {}),
        _config(tmp_path).tasks[0],
        SCHEMA,
        lose_lease,
    )
    assert (tmp_path / "terminated").read_text(encoding="utf-8") == "yes"
    assert renewals == 1
    assert outcome.outcome == "failure"
    assert outcome.payload == {
        "dispatcher": {"status": "failure", "code": "lease_lost", "retryAgent": False}
    }


def test_child_environment_has_explicit_allowlist() -> None:
    filtered = child_environment(
        {
            "PATH": "/bin",
            "CODEX_HOME": "/codex",
            "OPENAI_API_KEY": "auth",
            "MULTIPL_TOKEN": "private",
            "RANDOM_TOKEN": "private",
        }
    )
    assert filtered == {"PATH": "/bin", "CODEX_HOME": "/codex", "OPENAI_API_KEY": "auth"}
