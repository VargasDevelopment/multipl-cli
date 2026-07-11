from __future__ import annotations

import json
import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import jsonschema

from multipl_cli.private_dispatch.storage import atomic_write, ensure_private_dir
from multipl_cli.private_dispatch.types import Attempt, TaskPolicy, Work

_PRESERVED_ENV = {
    "CODEX_HOME",
    "HOME",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "LANG",
    "LC_ALL",
    "LOGNAME",
    "NO_PROXY",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "PATH",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TEMP",
    "TMP",
    "TMPDIR",
    "USER",
    "XDG_CONFIG_HOME",
}


@dataclass(frozen=True)
class AgentOutcome:
    attempt: Attempt
    payload: object
    outcome: str


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


def codex_argv(policy: TaskPolicy, schema_path: Path, output_path: Path) -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "-C",
        str(policy.cwd),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(output_path),
        "--model",
        policy.model,
        "--config",
        f'model_reasoning_effort="{policy.reasoning}"',
        "-",
    ]


def failure_payload(code: str) -> dict[str, object]:
    return {
        "dispatcher": {
            "status": "failure",
            "code": code,
            "retryAgent": False,
        }
    }


class AgentRunner:
    def __init__(self, state_dir: Path, heartbeat_seconds: float) -> None:
        self._artifacts = state_dir / "artifacts"
        self._heartbeat_seconds = heartbeat_seconds

    def run(
        self,
        attempt: Attempt,
        work: Work,
        policy: TaskPolicy,
        result_schema: dict[str, object],
        renew: Callable[[Attempt], Attempt],
    ) -> AgentOutcome:
        ensure_private_dir(self._artifacts)
        schema_path = self._artifacts / "output-schema.json"
        output_path = self._artifacts / "output-last-message.json"
        schema = json.dumps(result_schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
        atomic_write(schema_path, schema)
        atomic_write(output_path, b"")
        process = subprocess.Popen(
            codex_argv(policy, schema_path, output_path),
            cwd=policy.cwd,
            env=child_environment(dict(os.environ)),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
        )
        if process.stdin is None:
            self._terminate(process)
            return AgentOutcome(attempt, failure_payload("agent_stdin_unavailable"), "failure")
        process.stdin.write(deterministic_prompt(work))
        process.stdin.close()
        current = attempt
        lease_lost = False
        while process.poll() is None:
            try:
                process.wait(timeout=self._heartbeat_seconds)
            except subprocess.TimeoutExpired:
                try:
                    current = renew(current)
                except Exception:
                    lease_lost = True
                    self._terminate(process)
                    break
        if lease_lost:
            return AgentOutcome(current, failure_payload("lease_lost"), "failure")
        if process.returncode != 0:
            return AgentOutcome(current, failure_payload("agent_failed"), "failure")
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            jsonschema.validate(payload, result_schema)
        except (OSError, json.JSONDecodeError, jsonschema.ValidationError, jsonschema.SchemaError):
            return AgentOutcome(current, failure_payload("invalid_agent_output"), "failure")
        return AgentOutcome(current, payload, "success")

    @staticmethod
    def _terminate(process: subprocess.Popen[str]) -> None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
            process.wait()
