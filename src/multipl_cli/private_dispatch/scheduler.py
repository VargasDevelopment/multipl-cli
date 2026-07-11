from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass

from multipl_cli.private_dispatch.agent import (
    AgentRunner,
    RenewalUnresolved,
    clear_process_record,
    process_identity_from_journal,
    terminate_process_identity,
)
from multipl_cli.private_dispatch.client import PrivateApiError, PrivateClient
from multipl_cli.private_dispatch.lease import LeaseExpired, renewal_timeout
from multipl_cli.private_dispatch.storage import DispatchLockHeld, Journal, acquire_lock
from multipl_cli.private_dispatch.types import (
    TERMINAL_CODES,
    Attempt,
    DispatchConfig,
    Lease,
    PendingOutcome,
    PendingResult,
    ProcessIdentity,
    TaskContract,
    TaskIdentity,
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
        or not attempt_id
        or not isinstance(work_id, str)
        or not work_id
        or not isinstance(lease_id, str)
        or not lease_id
        or isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation <= 0
        or not isinstance(expires_at, str)
        or not expires_at
    ):
        raise ValueError("Journal attempt fields are invalid")
    return Attempt(attempt_id, work_id, Lease(lease_id, generation, expires_at))


def _identity_payload(identity: TaskIdentity) -> dict[str, object]:
    return identity.to_api()


def _identity_from(payload: object) -> TaskIdentity:
    if not isinstance(payload, dict):
        raise ValueError("Journal allowlist identity is invalid")
    registry_id = payload.get("registryId")
    type_id = payload.get("typeId")
    version = payload.get("version")
    if (
        not isinstance(registry_id, str)
        or not registry_id
        or not isinstance(type_id, str)
        or not type_id
        or isinstance(version, bool)
        or not isinstance(version, int)
        or version <= 0
    ):
        raise ValueError("Journal allowlist identity fields are invalid")
    return TaskIdentity(registry_id, type_id, version)


def _allowlist_from(payload: object) -> tuple[TaskIdentity, ...]:
    if not isinstance(payload, list):
        raise ValueError("Journal acquire allowlist is invalid")
    identities = tuple(_identity_from(item) for item in payload)
    if not identities:
        raise ValueError("Journal acquire allowlist is empty")
    return identities


def _pending_result_from(payload: dict[str, object]) -> PendingResult:
    key = payload.get("idempotencyKey")
    if not isinstance(key, str) or not key or "payload" not in payload:
        raise ValueError("Pending result journal is invalid")
    return PendingResult(_attempt_from(payload.get("attempt")), payload["payload"], key)


def _pending_outcome_from(payload: dict[str, object]) -> PendingOutcome:
    key = payload.get("idempotencyKey")
    outcome = payload.get("outcome")
    code = payload.get("code")
    if (
        not isinstance(key, str)
        or not key
        or outcome not in {"failed", "unknown"}
        or not isinstance(code, str)
        or code not in TERMINAL_CODES
    ):
        raise ValueError("Pending outcome journal is invalid")
    return PendingOutcome(_attempt_from(payload.get("attempt")), outcome, code, key)


def _launched_payload(
    attempt: Attempt,
    task_key: str,
    process: ProcessIdentity | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "state": "launched",
        "attempt": _attempt_payload(attempt),
        "taskKey": task_key,
    }
    if process is not None:
        payload["process"] = process.to_journal()
    return payload


class Dispatcher:
    def __init__(
        self,
        config: DispatchConfig,
        client: PrivateClient,
        runner: AgentRunner | None = None,
    ) -> None:
        self._config = config
        self._client = client
        self._journal = Journal(config.state_dir)
        self._runner = runner or AgentRunner(
            config.state_dir,
            config.heartbeat_seconds,
            on_process_started=self._record_process,
        )

    def dispatch_once(self) -> DispatchResult:
        try:
            lock = acquire_lock(self._config.state_dir)
        except DispatchLockHeld:
            return DispatchResult(0, "Private dispatch already running; no work acquired.")
        with lock:
            try:
                recovered = self._reconcile()
            except PrivateApiError as exc:
                journal = self._journal.load()
                if exc.operation == "acquire" or (
                    journal is not None and journal.get("state") == "acquire_intent"
                ):
                    return DispatchResult(2, "Acquire is pending; the exact request will be replayed.")
                raise
            if isinstance(recovered, DispatchResult):
                return recovered
            if recovered is None:
                contracts = {item.identity.key: item for item in self._client.task_contracts()}
                policies = {item.identity.key: item for item in self._config.tasks}
                if any(key not in contracts for key in policies):
                    return DispatchResult(2, "Configured task allowlist does not match the private registry.")
                allowlist = tuple(item.identity for item in self._config.tasks)
                try:
                    attempt = self._acquire(allowlist)
                except PrivateApiError:
                    return DispatchResult(2, "Acquire is pending; the exact request will be replayed.")
                if attempt is None:
                    return DispatchResult(0, "No private work available.")
                return self._execute(attempt, policies, contracts)

            contracts = {item.identity.key: item for item in self._client.task_contracts()}
            policies = {item.identity.key: item for item in self._config.tasks}
            if any(key not in contracts for key in policies):
                return DispatchResult(2, "Configured task allowlist does not match the private registry.")
            return self._execute(recovered, policies, contracts)

    def _reconcile(self) -> Attempt | DispatchResult | None:
        payload = self._journal.load()
        if payload is None:
            return None
        state = payload.get("state")
        if state == "acquire_intent":
            return self._replay_acquire(payload)
        if state == "acquire_response":
            return self._advance_acquire_response(payload)
        if state == "result_pending":
            pending = _pending_result_from(payload)
            try:
                self._client.submit(pending.attempt, pending.payload, pending.idempotency_key)
            except PrivateApiError:
                return DispatchResult(2, "Pending private result submission failed; no work acquired.")
            self._journal.clear()
            return None
        if state == "outcome_pending":
            pending = _pending_outcome_from(payload)
            try:
                self._client.outcome(
                    pending.attempt,
                    pending.outcome,
                    pending.code,
                    pending.idempotency_key,
                )
            except PrivateApiError:
                return DispatchResult(2, "Pending terminal outcome failed; no work acquired.")
            self._journal.clear()
            return None
        if state == "renew_intent":
            return self._replay_renew(payload)
        if state == "claimed":
            attempt = _attempt_from(payload.get("attempt"))
            return self._queue_and_flush_outcome(attempt, "failed", "restart_after_claim")
        if state == "launched":
            attempt = _attempt_from(payload.get("attempt"))
            self._terminate_journal_process(payload)
            return self._queue_and_flush_outcome(attempt, "unknown", "restart_after_launch")
        raise ValueError("Dispatcher journal state is invalid")

    def _acquire(self, allowlist: tuple[TaskIdentity, ...]) -> Attempt | None:
        key = _operation_key(
            "acquire",
            uuid.uuid4().hex,
            self._config.base_url,
            self._config.namespace,
            self._config.lane,
            tuple(item.key for item in allowlist),
        )
        intent = {
            "state": "acquire_intent",
            "allowlist": [_identity_payload(item) for item in allowlist],
            "idempotencyKey": key,
        }
        self._journal.write(intent)
        return self._replay_acquire(intent)

    def _replay_acquire(self, payload: dict[str, object]) -> Attempt | None:
        allowlist = _allowlist_from(payload.get("allowlist"))
        key = payload.get("idempotencyKey")
        if not isinstance(key, str) or not key:
            raise ValueError("Journal acquire idempotency key is invalid")
        attempt = self._client.acquire(allowlist, key)
        response = {
            "state": "acquire_response",
            "allowlist": [_identity_payload(item) for item in allowlist],
            "idempotencyKey": key,
            "attempt": _attempt_payload(attempt) if attempt is not None else None,
        }
        self._journal.write(response)
        return self._advance_acquire_response(response)

    def _advance_acquire_response(self, payload: dict[str, object]) -> Attempt | None:
        _allowlist_from(payload.get("allowlist"))
        key = payload.get("idempotencyKey")
        if not isinstance(key, str) or not key:
            raise ValueError("Journal acquire response idempotency key is invalid")
        raw_attempt = payload.get("attempt")
        if raw_attempt is None:
            self._journal.clear()
            return None
        attempt = _attempt_from(raw_attempt)
        self._journal.write({"state": "claimed", "attempt": _attempt_payload(attempt)})
        return attempt

    def _record_process(self, identity: ProcessIdentity) -> None:
        payload = self._journal.load()
        if payload is None or payload.get("state") != "launched":
            raise ValueError("Cannot record a process outside the launched journal state")
        payload["process"] = identity.to_journal()
        self._journal.write(payload)

    def _execute(
        self,
        attempt: Attempt,
        policies: dict[str, TaskPolicy],
        contracts: dict[str, TaskContract],
    ) -> DispatchResult:
        try:
            work = self._client.work(attempt.work_id)
        except PrivateApiError:
            return self._terminal_result(
                self._queue_and_flush_outcome(attempt, "failed", "work_unavailable")
            )
        if work.work_id != attempt.work_id or work.task.key not in policies:
            return self._terminal_result(
                self._queue_and_flush_outcome(attempt, "failed", "work_not_allowlisted")
            )
        policy = policies[work.task.key]
        contract = contracts.get(work.task.key)
        if contract is None:
            return self._terminal_result(
                self._queue_and_flush_outcome(attempt, "failed", "work_not_allowlisted")
            )
        self._journal.write(_launched_payload(attempt, work.task.key))

        def renew(current: Attempt) -> Attempt:
            key = _operation_key(
                "renew",
                current.work_id,
                current.attempt_id,
                current.lease.lease_id,
                current.lease.generation,
            )
            prior = self._journal.load()
            process = None
            if prior is not None:
                raw_process = prior.get("process")
                if isinstance(raw_process, dict):
                    process = raw_process
            intent = {
                "state": "renew_intent",
                "taskKey": work.task.key,
                "attempt": _attempt_payload(current),
                "renewIntent": {
                    "attempt": _attempt_payload(current),
                    "idempotencyKey": key,
                },
                "process": process,
            }
            self._journal.write(intent)
            try:
                timeout = renewal_timeout(current.lease.expires_at)
                renewed = self._renew_remote(current, key, timeout)
            except PrivateApiError as exc:
                if not exc.ambiguous:
                    self._journal.write(_launched_payload(current, work.task.key, _process_from(process)))
                    raise
                try:
                    timeout = renewal_timeout(current.lease.expires_at)
                    renewed = self._renew_remote(current, key, timeout)
                except (PrivateApiError, LeaseExpired) as replay_error:
                    intent["terminal"] = {"outcome": "failed", "code": "renew_ambiguous"}
                    self._journal.write(intent)
                    raise RenewalUnresolved("Renewal response remained ambiguous") from replay_error
            except LeaseExpired:
                self._journal.write(_launched_payload(current, work.task.key, _process_from(process)))
                raise
            self._journal.write(_launched_payload(renewed, work.task.key, _process_from(process)))
            return renewed

        outcome = self._runner.run(attempt, work, policy, contract.result_schema, renew)
        if outcome.defer_terminal:
            return DispatchResult(2, "Lease renewal is unresolved; the exact renewal will be replayed.")
        if outcome.outcome == "success":
            return self._queue_and_flush_result(outcome.attempt, outcome.payload)
        terminal_outcome = outcome.outcome if outcome.outcome in {"failed", "unknown"} else "failed"
        code = outcome.code if outcome.code in TERMINAL_CODES else "agent_runner_error"
        return self._terminal_result(
            self._queue_and_flush_outcome(outcome.attempt, terminal_outcome, code)
        )

    @staticmethod
    def _terminal_result(result: DispatchResult | None) -> DispatchResult:
        return result or DispatchResult(2, "Private terminal outcome submitted.")

    def _renew_remote(self, attempt: Attempt, key: str, timeout: float) -> Attempt:
        try:
            return self._client.renew(attempt, key, timeout=timeout)
        except TypeError as exc:
            if "timeout" not in str(exc):
                raise
            return self._client.renew(attempt, key)

    def _queue_and_flush_result(self, attempt: Attempt, payload: object) -> DispatchResult:
        pending = PendingResult(
            attempt,
            payload,
            _operation_key(
                "result",
                attempt.work_id,
                attempt.attempt_id,
                attempt.lease.lease_id,
                attempt.lease.generation,
            ),
        )
        self._journal.write(
            {
                "state": "result_pending",
                "attempt": _attempt_payload(pending.attempt),
                "payload": pending.payload,
                "idempotencyKey": pending.idempotency_key,
            }
        )
        try:
            self._client.submit(pending.attempt, pending.payload, pending.idempotency_key)
        except PrivateApiError:
            return DispatchResult(2, "Private result submission failed and remains pending.")
        self._journal.clear()
        return DispatchResult(0, "Private work completed.")

    def _queue_and_flush_outcome(
        self,
        attempt: Attempt,
        outcome: str,
        code: str,
    ) -> DispatchResult | None:
        if outcome not in {"failed", "unknown"} or code not in TERMINAL_CODES:
            raise ValueError("Invalid terminal outcome")
        pending = PendingOutcome(
            attempt,
            outcome,
            code,
            _operation_key(
                "outcome",
                attempt.work_id,
                attempt.attempt_id,
                attempt.lease.lease_id,
                attempt.lease.generation,
                outcome,
                code,
            ),
        )
        self._journal.write(
            {
                "state": "outcome_pending",
                "attempt": _attempt_payload(pending.attempt),
                "outcome": pending.outcome,
                "code": pending.code,
                "idempotencyKey": pending.idempotency_key,
            }
        )
        try:
            self._client.outcome(
                pending.attempt,
                pending.outcome,
                pending.code,
                pending.idempotency_key,
            )
        except PrivateApiError:
            return DispatchResult(2, "Terminal outcome failed and remains pending.")
        self._journal.clear()
        return None

    def _replay_renew(self, payload: dict[str, object]) -> DispatchResult | None:
        attempt = _attempt_from(payload.get("attempt"))
        raw_intent = payload.get("renewIntent")
        if not isinstance(raw_intent, dict):
            raise ValueError("Journal renew intent is invalid")
        intent_attempt = _attempt_from(raw_intent.get("attempt"))
        if intent_attempt != attempt:
            raise ValueError("Journal renew intent does not match current lease")
        key = raw_intent.get("idempotencyKey")
        if not isinstance(key, str) or not key:
            raise ValueError("Journal renew idempotency key is invalid")
        task_key = payload.get("taskKey")
        if not isinstance(task_key, str) or not task_key:
            raise ValueError("Journal renew task key is invalid")
        self._terminate_journal_process(payload)
        try:
            renewed = self._renew_remote(attempt, key, renewal_timeout(attempt.lease.expires_at))
        except (PrivateApiError, LeaseExpired) as exc:
            if isinstance(exc, PrivateApiError) and exc.ambiguous:
                return DispatchResult(2, "Renewal is ambiguous; the exact request remains pending.")
            renewed = attempt
        self._journal.write(_launched_payload(renewed, task_key))
        terminal = payload.get("terminal")
        if isinstance(terminal, dict):
            outcome = terminal.get("outcome")
            code = terminal.get("code")
            if outcome in {"failed", "unknown"} and code in TERMINAL_CODES:
                result = self._queue_and_flush_outcome(renewed, outcome, code)
                return result
        result = self._queue_and_flush_outcome(renewed, "unknown", "restart_after_launch")
        return result

    def _terminate_journal_process(self, payload: dict[str, object]) -> None:
        raw_process = payload.get("process")
        if raw_process is None:
            record_path = self._config.state_dir / "process.json"
            try:
                record = json.loads(record_path.read_text(encoding="utf-8"))
            except (FileNotFoundError, OSError, json.JSONDecodeError):
                record = None
            if isinstance(record, dict):
                raw_process = record.get("process")
        if raw_process is not None:
            identity = process_identity_from_journal(raw_process)
            terminate_process_identity(identity)
        clear_process_record(self._config.state_dir)


def _process_from(value: object) -> ProcessIdentity | None:
    if value is None:
        return None
    return process_identity_from_journal(value)


def run_dispatch(config: DispatchConfig) -> DispatchResult:
    try:
        with PrivateClient(config) as client:
            return Dispatcher(config, client).dispatch_once()
    except (PrivateApiError, OSError, ValueError) as exc:
        return DispatchResult(2, str(exc))
