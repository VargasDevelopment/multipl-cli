from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

TERMINAL_CODES = frozenset(
    {
        "agent_failed",
        "agent_runner_error",
        "agent_stdin_unavailable",
        "dispatcher_interrupted",
        "invalid_agent_output",
        "isolation_failed",
        "isolation_unavailable",
        "lease_expired",
        "lease_lost",
        "lease_too_close",
        "process_record_failed",
        "restart_after_claim",
        "restart_after_launch",
        "renew_ambiguous",
        "work_not_allowlisted",
        "work_unavailable",
    }
)


@dataclass(frozen=True)
class TaskIdentity:
    registry_id: str
    type_id: str
    version: int

    @property
    def key(self) -> str:
        return f"{self.registry_id}/{self.type_id}@{self.version}"

    def to_api(self) -> dict[str, object]:
        return {
            "registryId": self.registry_id,
            "typeId": self.type_id,
            "version": self.version,
        }


@dataclass(frozen=True)
class TaskPolicy:
    identity: TaskIdentity
    model: str
    reasoning: str
    cwd: Path


@dataclass(frozen=True)
class DispatchConfig:
    base_url: str
    bearer: str
    namespace: str
    lane: str
    tasks: tuple[TaskPolicy, ...]
    state_dir: Path
    heartbeat_seconds: float


@dataclass(frozen=True)
class Lease:
    lease_id: str
    generation: int
    expires_at: str

    def request(self) -> dict[str, object]:
        return {"leaseId": self.lease_id, "generation": self.generation}


@dataclass(frozen=True)
class Attempt:
    attempt_id: str
    work_id: str
    lease: Lease


@dataclass(frozen=True)
class Work:
    work_id: str
    task: TaskIdentity
    input: dict[str, object]


@dataclass(frozen=True)
class TaskContract:
    identity: TaskIdentity
    result_schema: dict[str, object]


@dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    pgid: int
    start_time: int
    command_hash: str

    def to_journal(self) -> dict[str, object]:
        return {
            "pid": self.pid,
            "pgid": self.pgid,
            "startTime": self.start_time,
            "commandHash": self.command_hash,
        }


@dataclass(frozen=True)
class PendingResult:
    attempt: Attempt
    payload: object
    idempotency_key: str


@dataclass(frozen=True)
class PendingOutcome:
    attempt: Attempt
    outcome: str
    code: str
    idempotency_key: str
