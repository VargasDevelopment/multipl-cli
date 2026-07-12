from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import jsonschema

from multipl_cli.private_dispatch.client import PrivateApiError
from multipl_cli.private_dispatch.lease import LeaseExpired, launch_is_safe, renewal_delay
from multipl_cli.private_dispatch.storage import atomic_json, atomic_write, ensure_private_dir
from multipl_cli.private_dispatch.types import Attempt, ProcessIdentity, TaskPolicy, Work

_BWRAP = Path("/usr/bin/bwrap")
_PRESERVED_ENV = {
    "ALL_PROXY",
    "CODEX_HOME",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "LANG",
    "LC_ALL",
    "NO_PROXY",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT_ID",
    "PATH",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
}
_INNER_PATH = "/usr/local/bin:/usr/bin:/bin"


class RenewalUnresolved(RuntimeError):
    pass


class RenewalLeaseLost(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Renewal resolved without an active lease: {code}")


class AgentInterrupted(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentOutcome:
    attempt: Attempt
    payload: object | None
    outcome: str
    code: str | None = None
    defer_terminal: bool = False


def child_environment(source: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in source.items()
        if key in _PRESERVED_ENV and not key.startswith("MULTIPL_")
    }


def deterministic_prompt(work: Work) -> str:
    identity = json.dumps(work.task.to_api(), sort_keys=True, separators=(",", ":"))
    work_input = json.dumps(work.input, sort_keys=True, separators=(",", ":"))
    return (
        "Execute exactly one private Multipl work item.\n"
        f"Task identity: {identity}\n"
        f"Work input: {work_input}\n"
        "Use only the supplied task identity and input as the work scope. "
        "Return only one JSON value that conforms exactly to the provided output schema.\n"
    )


def codex_argv(
    policy: TaskPolicy,
    schema_path: Path,
    output_path: Path,
    *,
    executable: str = "/runtime/codex",
) -> list[str]:
    return [
        executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "-C",
        "/workspace",
        "--output-schema",
        "/exchange/output-schema.json",
        "--output-last-message",
        "/exchange/output-last-message.json",
        "--model",
        policy.model,
        "--config",
        f'model_reasoning_effort="{policy.reasoning}"',
        "-",
    ]


def failure_payload(code: str) -> dict[str, object]:
    """Keep failure details available to callers without submitting them as results."""
    return {
        "dispatcher": {
            "status": "failure",
            "code": code,
            "retryAgent": False,
        }
    }


def _attempt_exchange(state_dir: Path, attempt: Attempt) -> Path:
    token = hashlib.sha256(
        f"{attempt.work_id}\0{attempt.attempt_id}".encode("utf-8")
    ).hexdigest()
    return state_dir / "exchange" / token


def _process_record_path(state_dir: Path) -> Path:
    return state_dir / "process.json"


def _proc_start_time(pid: int) -> int:
    fields = Path(f"/proc/{pid}/stat").read_text(encoding="ascii").rstrip().split(None, 2)
    if len(fields) != 3:
        raise OSError("Cannot read process identity")
    rest = fields[2].split()
    if len(rest) <= 19:
        raise OSError("Cannot read process start time")
    return int(rest[19])


def _proc_command_hash(pid: int) -> str:
    command = Path(f"/proc/{pid}/cmdline").read_bytes()
    return hashlib.sha256(command).hexdigest()


def process_identity(process: subprocess.Popen[str]) -> ProcessIdentity:
    return ProcessIdentity(
        pid=process.pid,
        pgid=os.getpgid(process.pid),
        start_time=_proc_start_time(process.pid),
        command_hash=_proc_command_hash(process.pid),
    )


def process_identity_from_journal(value: object) -> ProcessIdentity:
    if not isinstance(value, dict):
        raise ValueError("Journal process identity is invalid")
    pid = value.get("pid")
    pgid = value.get("pgid")
    start_time = value.get("startTime")
    command_hash = value.get("commandHash")
    if (
        isinstance(pid, bool)
        or not isinstance(pid, int)
        or pid <= 1
        or isinstance(pgid, bool)
        or not isinstance(pgid, int)
        or pgid <= 1
        or isinstance(start_time, bool)
        or not isinstance(start_time, int)
        or start_time < 0
        or not isinstance(command_hash, str)
        or len(command_hash) != 64
    ):
        raise ValueError("Journal process identity fields are invalid")
    return ProcessIdentity(pid, pgid, start_time, command_hash)


def _identity_matches(identity: ProcessIdentity) -> bool:
    try:
        if _proc_start_time(identity.pid) != identity.start_time:
            return False
        if os.getpgid(identity.pid) != identity.pgid:
            return False
        return _proc_command_hash(identity.pid) == identity.command_hash
    except (OSError, ValueError):
        return False


def terminate_process_identity(identity: ProcessIdentity, *, grace_seconds: float = 5.0) -> bool:
    if not _identity_matches(identity):
        return False
    try:
        os.killpg(identity.pgid, signal.SIGTERM)
    except ProcessLookupError:
        return False
    deadline = time.monotonic() + grace_seconds
    while _identity_matches(identity) and time.monotonic() < deadline:
        time.sleep(0.02)
    if _identity_matches(identity):
        try:
            os.killpg(identity.pgid, signal.SIGKILL)
        except ProcessLookupError:
            return True
    return True


def _terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        pgid = os.getpgid(process.pid)
        if pgid <= 1:
            return
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            return
        process.wait()


def _unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def clear_process_record(state_dir: Path) -> None:
    _unlink(_process_record_path(state_dir))


def _host_codex_home(source: dict[str, str]) -> Path:
    configured = source.get("CODEX_HOME")
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".codex"


def _codex_executable(source: dict[str, str]) -> Path:
    executable = shutil.which("codex", path=source.get("PATH"))
    if executable is None:
        raise FileNotFoundError("Codex executable is not available")
    resolved = Path(executable).resolve()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise OSError("Codex executable is not a regular executable")
    return resolved


def _inner_environment(source: dict[str, str]) -> dict[str, str]:
    environment = {
        "CODEX_HOME": "/codex-home",
        "HOME": "/home/codex",
        "PATH": _INNER_PATH,
        "TEMP": "/tmp",
        "TMPDIR": "/tmp",
        "XDG_CONFIG_HOME": "/home/codex/.config",
    }
    for key in _PRESERVED_ENV - {
        "CODEX_HOME",
        "HOME",
        "PATH",
        "TEMP",
        "TMPDIR",
    }:
        if key in source:
            environment[key] = source[key]
    return environment


def _bwrap_argv(
    policy: TaskPolicy,
    schema_path: Path,
    output_path: Path,
    codex_path: Path,
    source_environment: dict[str, str],
) -> list[str]:
    cwd = policy.cwd.resolve()
    try:
        codex_relative = codex_path.relative_to(cwd)
    except ValueError:
        codex_inner = "/runtime/codex"
    else:
        codex_inner = f"/workspace/{codex_relative.as_posix()}"
    arguments = [
        str(_BWRAP),
        "--die-with-parent",
        "--unshare-pid",
        "--new-session",
        "--clearenv",
        "--ro-bind",
        "/usr",
        "/usr",
        "--ro-bind-try",
        "/lib",
        "/lib",
        "--ro-bind-try",
        "/lib64",
        "/lib64",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--dir",
        "/etc",
        "--dir",
        "/etc/ssl",
        "--dir",
        "/etc/pki",
        "--dir",
        "/etc/ca-certificates",
        "--ro-bind-try",
        "/etc/hosts",
        "/etc/hosts",
        "--ro-bind-try",
        "/etc/resolv.conf",
        "/etc/resolv.conf",
        "--ro-bind-try",
        "/etc/nsswitch.conf",
        "/etc/nsswitch.conf",
        "--ro-bind-try",
        "/etc/passwd",
        "/etc/passwd",
        "--ro-bind-try",
        "/etc/group",
        "/etc/group",
        "--ro-bind-try",
        "/etc/ssl/certs",
        "/etc/ssl/certs",
        "--ro-bind-try",
        "/etc/ca-certificates",
        "/etc/ca-certificates",
        "--dir",
        "/home",
        "--dir",
        "/home/codex",
        "--dir",
        "/home/codex/.config",
        "--dir",
        "/codex-home",
        "--dir",
        "/workspace",
        "--bind",
        str(cwd),
        "/workspace",
        "--dir",
        "/exchange",
        "--ro-bind",
        str(schema_path),
        "/exchange/output-schema.json",
        "--bind",
        str(output_path),
        "/exchange/output-last-message.json",
    ]
    auth_path = _host_codex_home(source_environment) / "auth.json"
    if auth_path.is_file():
        arguments.extend(["--ro-bind", str(auth_path), "/codex-home/auth.json"])
    if codex_inner == "/runtime/codex":
        arguments.extend(["--dir", "/runtime", "--ro-bind", str(codex_path), codex_inner])
    for key, value in sorted(_inner_environment(source_environment).items()):
        arguments.extend(["--setenv", key, value])
    arguments.extend(
        [
            "--chdir",
            "/workspace",
            "--",
            *codex_argv(policy, schema_path, output_path, executable=codex_inner),
        ]
    )
    return arguments


def _install_signal_handlers() -> dict[int, object]:
    if threading.current_thread() is not threading.main_thread():
        return {}

    def interrupt(_signum: int, _frame: object) -> None:
        raise AgentInterrupted("Dispatcher interrupted")

    previous: dict[int, object] = {}
    for signum in (signal.SIGTERM, signal.SIGINT):
        previous[signum] = signal.getsignal(signum)
        signal.signal(signum, interrupt)
    return previous


def _restore_signal_handlers(previous: dict[int, object]) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)


class AgentRunner:
    def __init__(
        self,
        state_dir: Path,
        heartbeat_seconds: float,
        on_process_started: Callable[[ProcessIdentity], None] | None = None,
    ) -> None:
        self._state_dir = state_dir
        self._heartbeat_seconds = heartbeat_seconds
        self._on_process_started = on_process_started
        self._process_record = _process_record_path(state_dir)

    def run(
        self,
        attempt: Attempt,
        work: Work,
        policy: TaskPolicy,
        result_schema: dict[str, object],
        renew: Callable[[Attempt], Attempt],
    ) -> AgentOutcome:
        process: subprocess.Popen[str] | None = None
        current = attempt
        previous_handlers = _install_signal_handlers()
        try:
            try:
                if not launch_is_safe(attempt.lease.expires_at):
                    return AgentOutcome(
                        attempt,
                        failure_payload("lease_too_close"),
                        "failed",
                        "lease_too_close",
                    )
            except LeaseExpired:
                return AgentOutcome(
                    attempt,
                    failure_payload("lease_expired"),
                    "failed",
                    "lease_expired",
                )
            if self._state_dir.resolve().is_relative_to(policy.cwd.resolve()):
                return AgentOutcome(
                    attempt,
                    failure_payload("isolation_unavailable"),
                    "failed",
                    "isolation_unavailable",
                )
            if not _BWRAP.is_file() or not os.access(_BWRAP, os.X_OK):
                return AgentOutcome(
                    attempt,
                    failure_payload("isolation_unavailable"),
                    "failed",
                    "isolation_unavailable",
                )
            ensure_private_dir(self._state_dir)
            exchange = _attempt_exchange(self._state_dir, attempt)
            ensure_private_dir(exchange)
            schema_path = exchange / "output-schema.json"
            output_path = exchange / "output-last-message.json"
            schema = json.dumps(result_schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
            atomic_write(schema_path, schema)
            atomic_write(output_path, b"")
            source_environment = child_environment(dict(os.environ))
            codex_path = _codex_executable(source_environment)
            arguments = _bwrap_argv(
                policy,
                schema_path,
                output_path,
                codex_path,
                source_environment,
            )
            if not launch_is_safe(attempt.lease.expires_at):
                return AgentOutcome(
                    attempt,
                    failure_payload("lease_too_close"),
                    "failed",
                    "lease_too_close",
                )
            process = subprocess.Popen(
                arguments,
                cwd=policy.cwd,
                env=source_environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                start_new_session=True,
            )
            identity = process_identity(process)
            atomic_json(
                self._process_record,
                {
                    "attemptId": attempt.attempt_id,
                    "workId": attempt.work_id,
                    "process": identity.to_journal(),
                },
            )
            if self._on_process_started is not None:
                self._on_process_started(identity)
            if process.stdin is None:
                return AgentOutcome(
                    current,
                    failure_payload("agent_stdin_unavailable"),
                    "failed",
                    "agent_stdin_unavailable",
                )
            process.stdin.write(deterministic_prompt(work))
            process.stdin.close()
            while process.poll() is None:
                delay = renewal_delay(current.lease.expires_at, self._heartbeat_seconds)
                try:
                    process.wait(timeout=delay)
                except subprocess.TimeoutExpired:
                    current = renew(current)
            if process.returncode != 0:
                return AgentOutcome(
                    current,
                    failure_payload("agent_failed"),
                    "failed",
                    "agent_failed",
                )
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
                jsonschema.validate(payload, result_schema)
            except (OSError, json.JSONDecodeError, jsonschema.ValidationError, jsonschema.SchemaError):
                return AgentOutcome(
                    current,
                    failure_payload("invalid_agent_output"),
                    "failed",
                    "invalid_agent_output",
                )
            return AgentOutcome(current, payload, "success")
        except AgentInterrupted:
            return AgentOutcome(
                current,
                failure_payload("dispatcher_interrupted"),
                "unknown",
                "dispatcher_interrupted",
                True,
            )
        except RenewalLeaseLost as exc:
            return AgentOutcome(
                current,
                failure_payload(exc.code),
                "unknown",
                exc.code,
            )
        except RenewalUnresolved:
            return AgentOutcome(
                current,
                failure_payload("renew_ambiguous"),
                "failed",
                "renew_ambiguous",
                True,
            )
        except LeaseExpired:
            return AgentOutcome(
                current,
                failure_payload("lease_expired"),
                "failed",
                "lease_expired",
            )
        except PrivateApiError:
            return AgentOutcome(current, failure_payload("lease_lost"), "failed", "lease_lost")
        except FileNotFoundError:
            return AgentOutcome(
                current,
                failure_payload("isolation_unavailable"),
                "failed",
                "isolation_unavailable",
            )
        except OSError:
            return AgentOutcome(
                current,
                failure_payload("isolation_failed" if process is None else "agent_runner_error"),
                "failed",
                "isolation_failed" if process is None else "agent_runner_error",
            )
        except Exception:
            return AgentOutcome(
                current,
                failure_payload("agent_runner_error"),
                "failed",
                "agent_runner_error",
            )
        finally:
            if process is not None:
                _terminate_process(process)
            _unlink(self._process_record)
            _restore_signal_handlers(previous_handlers)
