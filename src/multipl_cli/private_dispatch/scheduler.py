from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass

from multipl_cli.private_dispatch.agent import (
    AgentRunner,
    RenewalLeaseLost,
    RenewalUnresolved,
    clear_process_record,
    process_identity_from_journal,
    terminate_process_identity,
)
from multipl_cli.private_dispatch.client import PrivateApiError, PrivateClient
from multipl_cli.private_dispatch.journal_state import (
    AcquireIntent,
    AcquireResponse,
    Claimed,
    Launched,
    OutcomePending,
    OutcomeRejected,
    RenewIntent,
    ResultPending,
    TerminalDirective,
    TerminalOutcome,
    json_for_submission,
)
from multipl_cli.private_dispatch.lease import (
    RENEW_REPLAY_TIMEOUT_SECONDS,
    LeaseExpired,
    renewal_timeout,
)
from multipl_cli.private_dispatch.state_machine import JournalStateMachine
from multipl_cli.private_dispatch.storage import DispatchLockHeld, Journal, acquire_lock
from multipl_cli.private_dispatch.types import (
    TERMINAL_CODES,
    Attempt,
    DispatchConfig,
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


def _renew_failure_code(error: PrivateApiError) -> str:
    if error.status_code == 410:
        return "lease_expired"
    return "lease_lost"


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
        self._machine = JournalStateMachine(self._journal)
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
            self._machine = JournalStateMachine(self._journal)
            try:
                recovered = self._reconcile()
            except PrivateApiError as exc:
                if exc.operation == "acquire" or isinstance(self._machine.state, AcquireIntent):
                    return DispatchResult(
                        2, "Acquire is pending; the exact request will be replayed."
                    )
                raise
            if isinstance(recovered, DispatchResult):
                return recovered
            try:
                contracts, policies = self._contracts_and_policies()
            except ValueError as exc:
                return DispatchResult(2, str(exc))
            if recovered is None:
                allowlist = tuple(item.identity for item in self._config.tasks)
                try:
                    attempt = self._acquire(allowlist)
                except PrivateApiError:
                    return DispatchResult(
                        2, "Acquire is pending; the exact request will be replayed."
                    )
                if attempt is None:
                    return DispatchResult(0, "No private work available.")
                return self._execute(attempt, policies, contracts)
            return self._execute(recovered, policies, contracts)

    def _contracts_and_policies(
        self,
    ) -> tuple[dict[str, TaskContract], dict[str, TaskPolicy]]:
        contracts = {item.identity.key: item for item in self._client.task_contracts()}
        policies = {item.identity.key: item for item in self._config.tasks}
        if any(key not in contracts for key in policies):
            raise ValueError("Configured task allowlist does not match the private registry.")
        return contracts, policies

    def _reconcile(self) -> Attempt | DispatchResult | None:
        return self._machine.recover(self)

    def recover_ready(self) -> None:
        return None

    def recover_acquire_intent(self, state: AcquireIntent) -> Attempt | None:
        return self._replay_acquire(state)

    def recover_acquire_response(self, state: AcquireResponse) -> Attempt | None:
        return self._advance_acquire_response(state)

    def recover_claimed(self, state: Claimed) -> DispatchResult | None:
        return self._queue_and_flush_outcome(state.attempt, "failed", "restart_after_claim")

    def recover_launched(self, state: Launched) -> DispatchResult | None:
        self._terminate_journal_process(state)
        return self._queue_and_flush_outcome(state.attempt, "unknown", "restart_after_launch")

    def recover_renew_intent(self, state: RenewIntent) -> DispatchResult | None:
        return self._replay_renew(state)

    def recover_result_pending(self, state: ResultPending) -> DispatchResult | None:
        try:
            self._client.submit(
                state.attempt,
                json_for_submission(state.payload),
                state.idempotency_key,
            )
        except PrivateApiError:
            return DispatchResult(2, "Pending private result submission failed; no work acquired.")
        self._machine.complete(state)
        return None

    def recover_outcome_pending(self, state: OutcomePending) -> DispatchResult | None:
        return self._flush_outcome(state)

    def recover_outcome_rejected(self, state: OutcomeRejected) -> DispatchResult:
        status = str(state.status_code) if state.status_code is not None else "unknown"
        return DispatchResult(
            2,
            f"Terminal outcome was definitively rejected (HTTP {status}); "
            "journal is fail-closed and requires operator reconciliation.",
        )

    def _acquire(self, allowlist: tuple[TaskIdentity, ...]) -> Attempt | None:
        key = _operation_key(
            "acquire",
            uuid.uuid4().hex,
            self._config.base_url,
            self._config.namespace,
            self._config.lane,
            tuple(item.key for item in allowlist),
        )
        intent = self._machine.begin_acquire(allowlist, key)
        return self._replay_acquire(intent)

    def _replay_acquire(self, state: AcquireIntent) -> Attempt | None:
        attempt = self._client.acquire(state.allowlist, state.idempotency_key)
        response = self._machine.record_acquire_response(state, attempt)
        return self._advance_acquire_response(response)

    def _advance_acquire_response(self, state: AcquireResponse) -> Attempt | None:
        claimed = self._machine.advance_acquire(state)
        return None if claimed is None else claimed.attempt

    def _record_process(self, identity: ProcessIdentity) -> None:
        launched = self._machine.require(Launched)
        self._machine.record_process(launched, identity)

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
        claimed = self._machine.require(Claimed)
        self._machine.launch(claimed, work.task.key)

        def renew(current: Attempt) -> Attempt:
            return self._renew(current)

        outcome = self._runner.run(attempt, work, policy, contract.result_schema, renew)
        if outcome.defer_terminal:
            return DispatchResult(
                2, "Lease renewal is unresolved; the exact renewal will be replayed."
            )
        if outcome.outcome == "success":
            return self._queue_and_flush_result(outcome.attempt, outcome.payload)
        terminal_outcome: TerminalOutcome = (
            outcome.outcome if outcome.outcome in {"failed", "unknown"} else "failed"
        )
        code = outcome.code if outcome.code in TERMINAL_CODES else "agent_runner_error"
        return self._terminal_result(
            self._queue_and_flush_outcome(outcome.attempt, terminal_outcome, code)
        )

    def _renew(self, current: Attempt) -> Attempt:
        launched = self._machine.require(Launched)
        if launched.attempt != current:
            raise ValueError("Renewal attempt does not match the journal lease")
        key = _operation_key(
            "renew",
            current.work_id,
            current.attempt_id,
            current.lease.lease_id,
            current.lease.generation,
        )
        intent = self._machine.begin_renew(launched, key)
        try:
            renewed = self._renew_remote(current, key, renewal_timeout(current.lease.expires_at))
        except PrivateApiError as first_error:
            if not first_error.ambiguous:
                self._machine.finish_renew(intent, current)
                raise
            try:
                renewed = self._renew_remote(
                    current, key, renewal_timeout(current.lease.expires_at)
                )
            except PrivateApiError as replay_error:
                if replay_error.ambiguous:
                    self._machine.defer_renew_terminal(
                        intent,
                        TerminalDirective("failed", "renew_ambiguous"),
                    )
                    raise RenewalUnresolved("Renewal response remained ambiguous") from replay_error
                raise RenewalLeaseLost(_renew_failure_code(replay_error)) from replay_error
            except LeaseExpired as replay_error:
                raise RenewalLeaseLost("lease_expired") from replay_error
        except LeaseExpired:
            self._machine.finish_renew(intent, current)
            raise
        self._machine.finish_renew(intent, renewed)
        return renewed

    def _renew_remote(self, attempt: Attempt, key: str, timeout: float) -> Attempt:
        return self._client.renew(attempt, key, timeout=timeout)

    def _queue_and_flush_result(self, attempt: Attempt, payload: object) -> DispatchResult:
        launched = self._machine.require(Launched)
        if launched.attempt != attempt:
            raise ValueError("Result attempt does not match the journal lease")
        pending = self._machine.queue_result(
            launched,
            payload,
            _operation_key(
                "result",
                attempt.work_id,
                attempt.attempt_id,
                attempt.lease.lease_id,
                attempt.lease.generation,
            ),
        )
        try:
            self._client.submit(
                pending.attempt,
                json_for_submission(pending.payload),
                pending.idempotency_key,
            )
        except PrivateApiError:
            return DispatchResult(2, "Private result submission failed and remains pending.")
        self._machine.complete(pending)
        return DispatchResult(0, "Private work completed.")

    def _queue_and_flush_outcome(
        self,
        attempt: Attempt,
        outcome: TerminalOutcome,
        code: str,
    ) -> DispatchResult | None:
        if (
            not isinstance(outcome, str)
            or outcome not in {"failed", "unknown"}
            or not isinstance(code, str)
            or code not in TERMINAL_CODES
        ):
            raise ValueError("Invalid terminal outcome code")
        current = self._machine.state
        if not isinstance(current, (Claimed, Launched, RenewIntent)) or current.attempt != attempt:
            raise ValueError("Terminal outcome attempt does not match the journal state")
        pending = self._machine.queue_outcome(
            current,
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
        return self._flush_outcome(pending)

    def _flush_outcome(self, pending: OutcomePending) -> DispatchResult | None:
        try:
            self._client.outcome(
                pending.attempt,
                pending.outcome,
                pending.code,
                pending.idempotency_key,
            )
        except PrivateApiError as exc:
            if exc.ambiguous:
                return DispatchResult(2, "Terminal outcome failed and remains pending.")
            self._machine.reject_outcome(pending, exc.status_code)
            status = str(exc.status_code) if exc.status_code is not None else "unknown"
            return DispatchResult(
                2,
                f"Terminal outcome was definitively rejected (HTTP {status}); "
                "journal is fail-closed and requires operator reconciliation.",
            )
        self._machine.complete(pending)
        return None

    @staticmethod
    def _terminal_result(result: DispatchResult | None) -> DispatchResult:
        return result or DispatchResult(2, "Private terminal outcome submitted.")

    def _replay_renew(self, state: RenewIntent) -> DispatchResult | None:
        self._terminate_journal_process(state)
        try:
            renewed = self._renew_remote(
                state.attempt,
                state.idempotency_key,
                RENEW_REPLAY_TIMEOUT_SECONDS,
            )
        except PrivateApiError as exc:
            if exc.ambiguous:
                return DispatchResult(2, "Renewal is ambiguous; the exact request remains pending.")
            return self._queue_and_flush_outcome(
                state.attempt,
                "unknown",
                _renew_failure_code(exc),
            )
        except LeaseExpired:
            return self._queue_and_flush_outcome(state.attempt, "unknown", "lease_expired")
        launched = self._machine.finish_renew(state, renewed)
        terminal = state.terminal
        if terminal is None:
            return self._queue_and_flush_outcome(
                launched.attempt,
                "unknown",
                "restart_after_launch",
            )
        return self._queue_and_flush_outcome(
            launched.attempt,
            terminal.outcome,
            terminal.code,
        )

    def _terminate_journal_process(self, state: Launched | RenewIntent) -> None:
        identity = state.process
        if identity is None:
            record_path = self._config.state_dir / "process.json"
            try:
                record = json.loads(record_path.read_text(encoding="utf-8"))
            except (FileNotFoundError, OSError, json.JSONDecodeError):
                record = None
            if isinstance(record, dict):
                identity = process_identity_from_journal(record.get("process"))
        if identity is not None:
            terminate_process_identity(identity)
        clear_process_record(self._config.state_dir)


def run_dispatch(config: DispatchConfig) -> DispatchResult:
    try:
        with PrivateClient(config) as client:
            return Dispatcher(config, client).dispatch_once()
    except (PrivateApiError, OSError, ValueError) as exc:
        return DispatchResult(2, str(exc))
