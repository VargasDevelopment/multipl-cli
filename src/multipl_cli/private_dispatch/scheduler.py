from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from multipl_cli.private_dispatch.agent import AgentRunner, failure_payload
from multipl_cli.private_dispatch.client import PrivateApiError, PrivateClient
from multipl_cli.private_dispatch.storage import DispatchLockHeld, Journal, acquire_lock
from multipl_cli.private_dispatch.types import (
    Attempt,
    DispatchConfig,
    Lease,
    PendingResult,
    TaskContract,
    TaskPolicy,
)


@dataclass(frozen=True)
class DispatchResult:
    code: int
    message: str


def _operation_key(operation: str, *parts: object) -> str:
    raw = "\0".join([operation, *(str(part) for part in parts)])
    return f"multipl-dispatch-{operation}-{hashlib.sha256(raw.encode()).hexdigest()}"


def _attempt_payload(attempt: Attempt) -> dict[str, object]:
    return {
        "attemptId": attempt.attempt_id,
        "workId": attempt.work_id,
        "lease": {
            "leaseId": attempt.lease.lease_id,
            "generation": attempt.lease.generation,
            "expiresAt": attempt.lease.expires_at,
        },
    }


def _attempt_from(payload: object) -> Attempt:
    if not isinstance(payload, dict):
        raise ValueError("Journal attempt is invalid")
    lease = payload.get("lease")
    if not isinstance(lease, dict):
        raise ValueError("Journal lease is invalid")
    attempt_id = payload.get("attemptId")
    work_id = payload.get("workId")
    lease_id = lease.get("leaseId")
    generation = lease.get("generation")
    expires_at = lease.get("expiresAt")
    if (
        not isinstance(attempt_id, str)
        or not isinstance(work_id, str)
        or not isinstance(lease_id, str)
        or isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation <= 0
        or not isinstance(expires_at, str)
    ):
        raise ValueError("Journal attempt fields are invalid")
    return Attempt(attempt_id, work_id, Lease(lease_id, generation, expires_at))


def _pending_from(payload: dict[str, object]) -> PendingResult:
    key = payload.get("idempotencyKey")
    outcome = payload.get("outcome")
    if not isinstance(key, str) or not isinstance(outcome, str) or "payload" not in payload:
        raise ValueError("Pending result journal is invalid")
    return PendingResult(_attempt_from(payload.get("attempt")), payload["payload"], key, outcome)


def _pending_payload(pending: PendingResult) -> dict[str, object]:
    return {
        "state": "result_pending",
        "attempt": _attempt_payload(pending.attempt),
        "payload": pending.payload,
        "idempotencyKey": pending.idempotency_key,
        "outcome": pending.outcome,
    }


class Dispatcher:
    def __init__(
        self,
        config: DispatchConfig,
        client: PrivateClient,
        runner: AgentRunner | None = None,
    ) -> None:
        self._config = config
        self._client = client
        self._runner = runner or AgentRunner(config.state_dir, config.heartbeat_seconds)
        self._journal = Journal(config.state_dir)

    def dispatch_once(self) -> DispatchResult:
        try:
            lock = acquire_lock(self._config.state_dir)
        except DispatchLockHeld:
            return DispatchResult(0, "Private dispatch already running; no work acquired.")
        with lock:
            pending_result = self._flush_or_reconcile()
            if pending_result is not None:
                return pending_result
            contracts = {item.identity.key: item for item in self._client.task_contracts()}
            policies = {item.identity.key: item for item in self._config.tasks}
            if any(key not in contracts for key in policies):
                return DispatchResult(2, "Configured task allowlist does not match the private registry.")
            attempt = self._client.acquire(
                tuple(item.identity for item in self._config.tasks),
                f"multipl-dispatch-acquire-{uuid.uuid4().hex}",
            )
            if attempt is None:
                return DispatchResult(0, "No private work available.")
            self._journal.write({"state": "claimed", "attempt": _attempt_payload(attempt)})
            return self._execute(attempt, policies, contracts)

    def _flush_or_reconcile(self) -> DispatchResult | None:
        payload = self._journal.load()
        if payload is None:
            return None
        state = payload.get("state")
        if state == "result_pending":
            pending = _pending_from(payload)
        elif state in {"claimed", "launched"}:
            attempt = _attempt_from(payload.get("attempt"))
            code = "restart_after_launch" if state == "launched" else "restart_after_claim"
            pending = PendingResult(
                attempt=attempt,
                payload=failure_payload(code),
                idempotency_key=_operation_key("result", attempt.work_id, attempt.attempt_id, code),
                outcome="unknown" if state == "launched" else "failure",
            )
            self._journal.write(_pending_payload(pending))
        else:
            raise ValueError("Dispatcher journal state is invalid")
        try:
            self._client.submit(pending.attempt, pending.payload, pending.idempotency_key)
        except PrivateApiError:
            return DispatchResult(2, "Pending private result submission failed; no work acquired.")
        self._journal.clear()
        return None

    def _execute(
        self,
        attempt: Attempt,
        policies: dict[str, TaskPolicy],
        contracts: dict[str, TaskContract],
    ) -> DispatchResult:
        work = self._client.work(attempt.work_id)
        if work.work_id != attempt.work_id or work.task.key not in policies:
            return self._record_and_submit(attempt, failure_payload("work_not_allowlisted"), "failure")
        policy = policies[work.task.key]
        contract = contracts[work.task.key]
        self._journal.write(
            {
                "state": "launched",
                "attempt": _attempt_payload(attempt),
                "taskKey": work.task.key,
            }
        )

        def renew(current: Attempt) -> Attempt:
            key = _operation_key(
                "renew",
                current.work_id,
                current.attempt_id,
                current.lease.generation,
            )
            renewed = self._client.renew(current, key)
            self._journal.write(
                {
                    "state": "launched",
                    "attempt": _attempt_payload(renewed),
                    "taskKey": work.task.key,
                }
            )
            return renewed

        outcome = self._runner.run(attempt, work, policy, contract.result_schema, renew)
        return self._record_and_submit(outcome.attempt, outcome.payload, outcome.outcome)

    def _record_and_submit(
        self, attempt: Attempt, payload: object, outcome: str
    ) -> DispatchResult:
        pending = PendingResult(
            attempt=attempt,
            payload=payload,
            idempotency_key=_operation_key("result", attempt.work_id, attempt.attempt_id, outcome),
            outcome=outcome,
        )
        self._journal.write(_pending_payload(pending))
        try:
            self._client.submit(attempt, payload, pending.idempotency_key)
        except PrivateApiError:
            return DispatchResult(2, "Private result submission failed and remains pending.")
        self._journal.clear()
        if outcome == "success":
            return DispatchResult(0, "Private work completed.")
        return DispatchResult(2, "Private work failed; failure result submitted.")


def run_dispatch(config: DispatchConfig) -> DispatchResult:
    try:
        with PrivateClient(config) as client:
            return Dispatcher(config, client).dispatch_once()
    except (PrivateApiError, OSError, ValueError) as exc:
        return DispatchResult(2, str(exc))
