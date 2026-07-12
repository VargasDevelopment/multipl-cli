from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from multipl_cli.private_dispatch.agent import (
    AgentOutcome,
    AgentRunner,
    RenewalLeaseLost,
    RenewalUnresolved,
    child_environment,
    process_identity,
)
from multipl_cli.private_dispatch.client import PrivateApiError
from multipl_cli.private_dispatch.journal_state import (
    AcquireIntent,
    AcquireResponse,
    Claimed,
    Launched,
    OutcomePending,
    OutcomeRejected,
    RenewIntent,
)
from multipl_cli.private_dispatch.lease import LeaseExpired
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
    worktree = tmp_path / "worktree"
    worktree.mkdir(parents=True, exist_ok=True)
    return DispatchConfig(
        base_url="https://private.multipl.test",
        bearer="secret-bearer",
        namespace="tenant-a",
        lane="agents",
        tasks=(TaskPolicy(IDENTITY, "gpt-5.6-codex", "high", worktree),),
        state_dir=tmp_path / "state",
        heartbeat_seconds=heartbeat,
    )


def _attempt(generation: int = 1, expires_at: str = "2030-01-01T00:00:00Z") -> Attempt:
    return Attempt(
        "attempt-1",
        "work-1",
        Lease("00000000-0000-4000-8000-000000000001", generation, expires_at),
    )


class FakeClient:
    def __init__(
        self,
        attempt: Attempt | None = None,
        submit_failures: int = 0,
        outcome_failures: int = 0,
        acquire_error: PrivateApiError | None = None,
        renew_errors: list[PrivateApiError] | None = None,
        outcome_errors: list[PrivateApiError] | None = None,
    ) -> None:
        self.next_attempt = attempt
        self.submit_failures = submit_failures
        self.outcome_failures = outcome_failures
        self.acquire_error = acquire_error
        self.renew_errors = list(renew_errors or [])
        self.outcome_errors = list(outcome_errors or [])
        self.acquires: list[tuple[tuple[TaskIdentity, ...], str]] = []
        self.submissions: list[tuple[Attempt, object, str]] = []
        self.outcomes: list[tuple[Attempt, str, str, str]] = []
        self.renews: list[tuple[Attempt, str, float | None]] = []

    def task_contracts(self) -> tuple[TaskContract, ...]:
        return (TaskContract(IDENTITY, SCHEMA),)

    def acquire(self, allowlist: tuple[TaskIdentity, ...], key: str) -> Attempt | None:
        self.acquires.append((allowlist, key))
        if self.acquire_error is not None:
            raise self.acquire_error
        value = self.next_attempt
        self.next_attempt = None
        return value

    def work(self, work_id: str) -> Work:
        assert work_id == "work-1"
        return Work(work_id, IDENTITY, {"document": "hello"})

    def renew(self, attempt: Attempt, key: str, *, timeout: float | None = None) -> Attempt:
        self.renews.append((attempt, key, timeout))
        if self.renew_errors:
            raise self.renew_errors.pop(0)
        return _attempt(attempt.lease.generation + 1)

    def submit(self, attempt: Attempt, payload: object, key: str) -> None:
        self.submissions.append((attempt, payload, key))
        if self.submit_failures:
            self.submit_failures -= 1
            raise PrivateApiError("submit result", 503, ambiguous=True)

    def outcome(self, attempt: Attempt, outcome: str, code: str, key: str) -> None:
        self.outcomes.append((attempt, outcome, code, key))
        if self.outcome_errors:
            raise self.outcome_errors.pop(0)
        if self.outcome_failures:
            self.outcome_failures -= 1
            raise PrivateApiError("submit outcome", 503, ambiguous=True)


class FakeRunner:
    def __init__(self, result: str = "success", code: str = "invalid_agent_output", call_renew: bool = False) -> None:
        self.calls = 0
        self.result = result
        self.code = code
        self.call_renew = call_renew

    def run(self, attempt, work, policy, result_schema, renew) -> AgentOutcome:
        self.calls += 1
        assert work.task == IDENTITY
        assert policy.cwd.is_absolute()
        assert result_schema == SCHEMA
        current = attempt
        if self.call_renew:
            try:
                current = renew(current)
            except RenewalUnresolved:
                return AgentOutcome(current, None, "failed", "renew_ambiguous", True)
            except RenewalLeaseLost as error:
                return AgentOutcome(current, None, "unknown", error.code)
            except LeaseExpired:
                return AgentOutcome(current, None, "failed", "lease_expired")
            except PrivateApiError:
                return AgentOutcome(current, None, "failed", "lease_lost")
        if self.result == "success":
            return AgentOutcome(current, {"result": "done"}, "success")
        outcome = "unknown" if self.result == "unknown" else "failed"
        return AgentOutcome(current, None, outcome, self.code)


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
    assert client.outcomes == []
    assert not Journal(_config(tmp_path).state_dir).path.exists()


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
    assert client.outcomes == []
    assert not Journal(_config(tmp_path).state_dir).path.exists()


def test_acquire_intent_replays_exact_allowlist_and_key_after_ambiguous_failure(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    first_client = FakeClient(acquire_error=PrivateApiError("acquire", 503, ambiguous=True))
    first = Dispatcher(config, first_client, FakeRunner()).dispatch_once()
    assert first.code == 2
    intent = Journal(config.state_dir).load()
    assert isinstance(intent, AcquireIntent)
    assert intent.allowlist == (IDENTITY,)
    key = intent.idempotency_key

    second_client = FakeClient(_attempt())
    second = Dispatcher(config, second_client, FakeRunner()).dispatch_once()
    assert second.code == 0
    assert second_client.acquires == [((IDENTITY,), key)]
    assert len(second_client.submissions) == 1


def test_acquire_response_is_replayed_without_a_second_acquire(tmp_path: Path) -> None:
    config = _config(tmp_path)
    attempt = _attempt()
    Journal(config.state_dir).write(AcquireResponse((IDENTITY,), "stable-acquire-key", attempt))
    client = FakeClient()
    result = Dispatcher(config, client, FakeRunner()).dispatch_once()
    assert result.code == 0
    assert client.acquires == []
    assert client.submissions[0][1] == {"result": "done"}


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


def test_failure_uses_terminal_endpoint_not_producer_result(tmp_path: Path) -> None:
    client = FakeClient(_attempt())
    result = Dispatcher(
        _config(tmp_path),
        client,
        FakeRunner(result="failed", code="invalid_agent_output"),
    ).dispatch_once()
    assert result.code == 2
    assert client.submissions == []
    assert client.outcomes[0][1:3] == ("failed", "invalid_agent_output")


def test_terminal_outcome_spool_blocks_acquire_until_retried(tmp_path: Path) -> None:
    config = _config(tmp_path)
    first_client = FakeClient(_attempt(), outcome_failures=1)
    first = Dispatcher(config, first_client, FakeRunner(result="failed")).dispatch_once()
    assert first.code == 2
    assert isinstance(Journal(config.state_dir).load(), OutcomePending)

    second_client = FakeClient()
    second = Dispatcher(config, second_client, FakeRunner()).dispatch_once()
    assert second.code == 0
    assert second_client.outcomes[0][3] == first_client.outcomes[0][3]
    assert len(second_client.acquires) == 1


def test_renewal_is_journaled_and_timeout_is_bounded_by_remaining_lease(tmp_path: Path) -> None:
    expires = (datetime.now(timezone.utc) + timedelta(seconds=2)).isoformat()
    client = FakeClient(_attempt(expires_at=expires))
    result = Dispatcher(
        _config(tmp_path, heartbeat=30), client, FakeRunner(call_renew=True)
    ).dispatch_once()
    assert result.code == 0
    assert len(client.renews) == 1
    assert 0 < client.renews[0][2] <= 2
    assert client.renews[0][0].lease.generation == 1
    assert not Journal(_config(tmp_path).state_dir).path.exists()


def test_ambiguous_renew_retries_exact_request_and_defers_terminal_state(tmp_path: Path) -> None:
    error = PrivateApiError("renew", ambiguous=True)
    config = _config(tmp_path)
    first_client = FakeClient(_attempt(), renew_errors=[error, error])
    first = Dispatcher(config, first_client, FakeRunner(call_renew=True)).dispatch_once()
    assert first.code == 2
    intent = Journal(config.state_dir).load()
    assert isinstance(intent, RenewIntent)
    assert intent.terminal is not None
    assert (intent.terminal.outcome, intent.terminal.code) == ("failed", "renew_ambiguous")
    assert first_client.renews[0][0] == first_client.renews[1][0]
    assert first_client.renews[0][1] == first_client.renews[1][1]

    second_client = FakeClient()
    second = Dispatcher(config, second_client, FakeRunner()).dispatch_once()
    assert second.code == 0
    assert second_client.renews[0][0].lease.generation == 1
    assert second_client.renews[0][1] == first_client.renews[0][1]
    assert second_client.outcomes[0][0].lease.generation == 2
    assert second_client.outcomes[0][1:3] == ("failed", "renew_ambiguous")


def test_exact_renew_replay_not_found_kills_child_and_submits_unknown_with_original_lease(
    tmp_path: Path,
) -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        start_new_session=True,
    )
    try:
        time.sleep(0.05)
        identity = process_identity(process)
        config = _config(tmp_path)
        attempt = _attempt(
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
        )
        Journal(config.state_dir).write(
            RenewIntent(attempt, IDENTITY.key, "stable-renew-key", identity)
        )
        client = FakeClient(renew_errors=[PrivateApiError("renew", 404)])

        result = Dispatcher(config, client, FakeRunner()).dispatch_once()

        assert result.code == 0
        for _ in range(50):
            if process.poll() is not None:
                break
            time.sleep(0.02)
        assert process.poll() is not None
        assert client.outcomes[0][:3] == (attempt, "unknown", "lease_lost")
        assert client.outcomes[0][0].lease.generation == 1
        assert client.renews == [(attempt, "stable-renew-key", pytest.approx(30, abs=1))]
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()


def test_in_process_renew_replay_not_found_becomes_unknown_with_original_lease(
    tmp_path: Path,
) -> None:
    attempt = _attempt()
    client = FakeClient(
        attempt,
        renew_errors=[
            PrivateApiError("renew", 503, ambiguous=True),
            PrivateApiError("renew", 404),
        ],
    )

    result = Dispatcher(_config(tmp_path), client, FakeRunner(call_renew=True)).dispatch_once()

    assert result.code == 2
    assert client.outcomes[0][:3] == (attempt, "unknown", "lease_lost")
    assert client.outcomes[0][0].lease.generation == 1
    assert client.renews[0][:2] == client.renews[1][:2]


def test_definitive_outcome_rejection_is_durable_and_does_not_loop(tmp_path: Path) -> None:
    config = _config(tmp_path)
    first_client = FakeClient(
        _attempt(),
        outcome_errors=[PrivateApiError("submit outcome", 404)],
    )
    first = Dispatcher(config, first_client, FakeRunner(result="failed")).dispatch_once()

    assert first.code == 2
    rejected = Journal(config.state_dir).load()
    assert isinstance(rejected, OutcomeRejected)
    assert rejected.status_code == 404

    second_client = FakeClient()
    second = Dispatcher(config, second_client, FakeRunner()).dispatch_once()

    assert second.code == 2
    assert "operator reconciliation" in second.message
    assert second_client.outcomes == []
    assert second_client.acquires == []


def test_restart_during_renew_replays_exact_lease_before_unknown_outcome(tmp_path: Path) -> None:
    config = _config(tmp_path)
    attempt = _attempt()
    key = "stable-renew-key"
    Journal(config.state_dir).write(RenewIntent(attempt, IDENTITY.key, key))
    client = FakeClient()
    result = Dispatcher(config, client, FakeRunner()).dispatch_once()
    assert result.code == 0
    assert client.renews[0][0] == attempt
    assert client.renews[0][1] == key
    assert client.outcomes[0][0].lease.generation == 2
    assert client.outcomes[0][1:3] == ("unknown", "restart_after_launch")


def test_restart_after_launch_submits_unknown_outcome_and_never_relaunches(tmp_path: Path) -> None:
    config = _config(tmp_path)
    journal = Journal(config.state_dir)
    journal.write(Launched(_attempt(), IDENTITY.key))
    client = FakeClient()
    runner = FakeRunner()
    result = Dispatcher(config, client, runner).dispatch_once()
    assert result.code == 0
    assert runner.calls == 0
    assert client.submissions == []
    assert client.outcomes[0][1:3] == ("unknown", "restart_after_launch")


def test_restart_after_launch_terminates_matching_recorded_process_group(tmp_path: Path) -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        start_new_session=True,
    )
    try:
        time.sleep(0.05)
        identity = process_identity(process)
        config = _config(tmp_path)
        attempt = _attempt()
        Journal(config.state_dir).write(Launched(attempt, IDENTITY.key, identity))
        result = Dispatcher(config, FakeClient(), FakeRunner()).dispatch_once()
        assert result.code == 0
        for _ in range(50):
            if process.poll() is not None:
                break
            time.sleep(0.02)
        assert process.poll() is not None
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()


def test_restart_after_claim_submits_failed_outcome_without_launch(tmp_path: Path) -> None:
    config = _config(tmp_path)
    Journal(config.state_dir).write(Claimed(_attempt()))
    client = FakeClient()
    runner = FakeRunner()
    result = Dispatcher(config, client, runner).dispatch_once()
    assert result.code == 0
    assert runner.calls == 0
    assert client.submissions == []
    assert client.outcomes[0][1:3] == ("failed", "restart_after_claim")


def _fake_codex(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "codex"
    executable.write_text("#!/usr/bin/python3\n" + body, encoding="utf-8")
    executable.chmod(0o700)
    return executable


def test_agent_bwrap_isolates_config_home_and_proc_but_allows_exchange_and_worktree(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "private.json"
    config_path.write_text('{"bearer":"real-bearer"}', encoding="utf-8")
    home = tmp_path / "codex-home"
    home.mkdir()
    (home / "auth.json").write_text('{"token":"auth-token"}', encoding="utf-8")
    unrelated = home / "unrelated.txt"
    unrelated.write_text("home-secret", encoding="utf-8")
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    body = f"""import json, os, sys
from pathlib import Path
args = sys.argv[1:]
def read(path):
    try:
        return Path(path).read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        return None
schema = json.load(open(args[args.index('--output-schema') + 1]))
capture = {{
    'args': args,
    'cwd': os.getcwd(),
    'env': dict(os.environ),
    'stdin': sys.stdin.read(),
    'schema': schema,
    'config': read({str(config_path)!r}),
    'state': read({str(tmp_path / 'state' / 'journal.json')!r}),
    'unrelated': read({str(unrelated)!r}),
    'auth': read(os.path.join(os.environ['CODEX_HOME'], 'auth.json')),
    'proc': read('/proc/1/cmdline'),
}}
Path('capture.json').write_text(json.dumps(capture), encoding='utf-8')
json.dump({{'result': 'done'}}, open(args[args.index('--output-last-message') + 1], 'w'))
"""
    _fake_codex(worktree, body)
    monkeypatch.setenv("PATH", f"{worktree}:{os.environ['PATH']}")
    monkeypatch.setenv("CODEX_HOME", str(home))
    monkeypatch.setenv("MULTIPL_BEARER", "real-bearer")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-leak")
    state = tmp_path / "state"
    policy = TaskPolicy(IDENTITY, "gpt-5.6-codex", "high", worktree)
    outcome = AgentRunner(state, 5).run(
        _attempt(),
        Work("work-1", IDENTITY, {"document": "hello"}),
        policy,
        SCHEMA,
        lambda attempt: attempt,
    )
    capture = json.loads((worktree / "capture.json").read_text(encoding="utf-8"))
    assert outcome.outcome == "success"
    assert outcome.payload == {"result": "done"}
    assert capture["cwd"] == "/workspace"
    assert capture["schema"] == SCHEMA
    assert '"document":"hello"' in capture["stdin"]
    assert capture["config"] is None
    assert capture["state"] is None
    assert capture["unrelated"] is None
    assert capture["auth"] == '{"token":"auth-token"}'
    assert "real-bearer" not in capture["proc"]
    assert all(not key.startswith("MULTIPL_") for key in capture["env"])
    assert "UNRELATED_SECRET" not in capture["env"]
    assert stat.S_IMODE(state.stat().st_mode) == 0o700
    exchange_output = next((state / "exchange").glob("*/output-last-message.json"))
    assert stat.S_IMODE(exchange_output.stat().st_mode) == 0o600
    assert not (state / "process.json").exists()


def test_lease_loss_terminates_agent_process_group(monkeypatch, tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    _fake_codex(
        worktree,
        """import time
from pathlib import Path
while True:
    Path('alive').write_text(str(time.time()))
    time.sleep(0.05)
""",
    )
    monkeypatch.setenv("PATH", f"{worktree}:{os.environ['PATH']}")
    runner = AgentRunner(tmp_path / "state", 0.25)

    renewals = 0

    def lose_lease(_attempt: Attempt) -> Attempt:
        nonlocal renewals
        renewals += 1
        raise PrivateApiError("renew", 404)

    outcome = runner.run(
        _attempt(),
        Work("work-1", IDENTITY, {}),
        TaskPolicy(IDENTITY, "gpt-5.6-codex", "high", worktree),
        SCHEMA,
        lose_lease,
    )
    alive = worktree / "alive"
    assert alive.exists()
    timestamp = alive.stat().st_mtime_ns
    time.sleep(0.2)
    assert alive.stat().st_mtime_ns == timestamp
    assert renewals == 1
    assert outcome.outcome == "failed"
    assert outcome.code == "lease_lost"


def test_agent_does_not_launch_when_lease_is_too_close(monkeypatch, tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    _fake_codex(worktree, "raise SystemExit('must not launch')\n")
    monkeypatch.setenv("PATH", f"{worktree}:{os.environ['PATH']}")
    expires = (datetime.now(timezone.utc) + timedelta(milliseconds=100)).isoformat()
    outcome = AgentRunner(tmp_path / "state", 1).run(
        _attempt(expires_at=expires),
        Work("work-1", IDENTITY, {}),
        TaskPolicy(IDENTITY, "gpt-5.6-codex", "high", worktree),
        SCHEMA,
        lambda attempt: attempt,
    )
    assert outcome.outcome == "failed"
    assert outcome.code == "lease_too_close"
    assert not (worktree / "capture.json").exists()


@pytest.mark.parametrize("parent_signal", [signal.SIGTERM, signal.SIGKILL])
def test_dispatcher_parent_death_does_not_leave_fake_agent_orphan(
    tmp_path: Path,
    parent_signal: signal.Signals,
) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    marker = worktree / "alive"
    _fake_codex(
        worktree,
        """import time
from pathlib import Path
while True:
    Path('alive').write_text(str(time.time()))
    time.sleep(0.05)
""",
    )
    state = tmp_path / "state"
    source_root = Path(__file__).resolve().parents[1] / "src"
    driver = f"""from pathlib import Path
from multipl_cli.private_dispatch.agent import AgentRunner
from multipl_cli.private_dispatch.types import Attempt, Lease, TaskIdentity, TaskPolicy, Work
identity = TaskIdentity('registry.id', 'document.index', 1)
worktree = Path({str(worktree)!r})
runner = AgentRunner(Path({str(state)!r}), 30)
runner.run(
    Attempt('attempt-1', 'work-1', Lease('lease-1', 1, '2030-01-01T00:00:00Z')),
    Work('work-1', identity, {{}}),
    TaskPolicy(identity, 'gpt-5.6-codex', 'high', worktree),
    {{'type': 'object'}},
    lambda attempt: attempt,
)
"""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(source_root)
    environment["PATH"] = f"{worktree}:{environment['PATH']}"
    driver_process = subprocess.Popen([sys.executable, "-c", driver], env=environment)
    try:
        for _ in range(100):
            if marker.exists():
                break
            time.sleep(0.05)
        assert marker.exists()
        driver_process.send_signal(parent_signal)
        driver_process.wait(timeout=10)
        time.sleep(0.2)
        timestamp = marker.stat().st_mtime_ns
        time.sleep(0.2)
        assert marker.stat().st_mtime_ns == timestamp
    finally:
        if driver_process.poll() is None:
            driver_process.kill()
            driver_process.wait()


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
