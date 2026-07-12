from __future__ import annotations

from dataclasses import replace
from typing import Protocol, TypeVar, assert_never

from multipl_cli.private_dispatch.journal_state import (
    AcquireIntent,
    AcquireResponse,
    Claimed,
    JournalState,
    Launched,
    OutcomePending,
    OutcomeRejected,
    RenewIntent,
    ResultPending,
    TerminalDirective,
    TerminalOutcome,
)
from multipl_cli.private_dispatch.storage import Journal
from multipl_cli.private_dispatch.types import (
    Attempt,
    ProcessIdentity,
    TaskIdentity,
)


class IllegalJournalTransition(ValueError):
    pass


LEGAL_TRANSITIONS: dict[type[object], frozenset[type[object]]] = {
    type(None): frozenset({AcquireIntent}),
    AcquireIntent: frozenset({AcquireResponse}),
    AcquireResponse: frozenset({Claimed, type(None)}),
    Claimed: frozenset({Launched, OutcomePending}),
    Launched: frozenset({Launched, RenewIntent, ResultPending, OutcomePending}),
    RenewIntent: frozenset({RenewIntent, Launched, OutcomePending}),
    ResultPending: frozenset({type(None)}),
    OutcomePending: frozenset({type(None), OutcomeRejected}),
    OutcomeRejected: frozenset(),
}
_ALLOWED_TRANSITIONS = LEGAL_TRANSITIONS


def transition_allowed(current: JournalState | None, target: JournalState | None) -> bool:
    return type(target) in _ALLOWED_TRANSITIONS.get(type(current), frozenset())


def validate_transition(current: JournalState | None, target: JournalState | None) -> None:
    if not transition_allowed(current, target):
        raise IllegalJournalTransition(
            f"Illegal dispatcher journal transition: {type(current).__name__} -> "
            f"{type(target).__name__}"
        )


RecoveryResult = TypeVar("RecoveryResult", covariant=True)
StateT = TypeVar("StateT")


class RecoveryHandler(Protocol[RecoveryResult]):
    def recover_ready(self) -> RecoveryResult: ...

    def recover_acquire_intent(self, state: AcquireIntent) -> RecoveryResult: ...

    def recover_acquire_response(self, state: AcquireResponse) -> RecoveryResult: ...

    def recover_claimed(self, state: Claimed) -> RecoveryResult: ...

    def recover_launched(self, state: Launched) -> RecoveryResult: ...

    def recover_renew_intent(self, state: RenewIntent) -> RecoveryResult: ...

    def recover_result_pending(self, state: ResultPending) -> RecoveryResult: ...

    def recover_outcome_pending(self, state: OutcomePending) -> RecoveryResult: ...

    def recover_outcome_rejected(self, state: OutcomeRejected) -> RecoveryResult: ...


def dispatch_recovery(
    state: JournalState | None,
    handler: RecoveryHandler[RecoveryResult],
) -> RecoveryResult:
    match state:
        case None:
            return handler.recover_ready()
        case AcquireIntent():
            return handler.recover_acquire_intent(state)
        case AcquireResponse():
            return handler.recover_acquire_response(state)
        case Claimed():
            return handler.recover_claimed(state)
        case Launched():
            return handler.recover_launched(state)
        case RenewIntent():
            return handler.recover_renew_intent(state)
        case ResultPending():
            return handler.recover_result_pending(state)
        case OutcomePending():
            return handler.recover_outcome_pending(state)
        case OutcomeRejected():
            return handler.recover_outcome_rejected(state)
    assert_never(state)


class JournalStateMachine:
    def __init__(self, journal: Journal) -> None:
        self._journal = journal
        self._state = journal.load()

    @property
    def state(self) -> JournalState | None:
        return self._state

    def recover(self, handler: RecoveryHandler[RecoveryResult]) -> RecoveryResult:
        return dispatch_recovery(self._state, handler)

    def require(self, state_type: type[StateT]) -> StateT:
        if not isinstance(self._state, state_type):
            raise IllegalJournalTransition(
                f"Expected {state_type.__name__}, found {type(self._state).__name__}"
            )
        return self._state

    def _commit(self, current: JournalState | None, target: JournalState | None) -> None:
        if self._state != current:
            raise IllegalJournalTransition("Dispatcher journal changed outside the state machine")
        validate_transition(current, target)
        if target is None:
            self._journal.clear()
        else:
            self._journal.write(target)
        self._state = target

    def begin_acquire(
        self,
        allowlist: tuple[TaskIdentity, ...],
        idempotency_key: str,
    ) -> AcquireIntent:
        target = AcquireIntent(allowlist, idempotency_key)
        self._commit(None, target)
        return target

    def record_acquire_response(
        self,
        current: AcquireIntent,
        attempt: Attempt | None,
    ) -> AcquireResponse:
        target = AcquireResponse(current.allowlist, current.idempotency_key, attempt)
        self._commit(current, target)
        return target

    def advance_acquire(self, current: AcquireResponse) -> Claimed | None:
        target = None if current.attempt is None else Claimed(current.attempt)
        self._commit(current, target)
        return target

    def launch(self, current: Claimed, task_key: str) -> Launched:
        target = Launched(current.attempt, task_key)
        self._commit(current, target)
        return target

    def record_process(self, current: Launched, process: ProcessIdentity) -> Launched:
        target = replace(current, process=process)
        self._commit(current, target)
        return target

    def begin_renew(self, current: Launched, idempotency_key: str) -> RenewIntent:
        target = RenewIntent(
            current.attempt,
            current.task_key,
            idempotency_key,
            current.process,
        )
        self._commit(current, target)
        return target

    def finish_renew(self, current: RenewIntent, attempt: Attempt) -> Launched:
        target = Launched(attempt, current.task_key, current.process)
        self._commit(current, target)
        return target

    def defer_renew_terminal(
        self,
        current: RenewIntent,
        terminal: TerminalDirective,
    ) -> RenewIntent:
        target = replace(current, terminal=terminal)
        self._commit(current, target)
        return target

    def queue_result(
        self,
        current: Launched,
        payload: object,
        idempotency_key: str,
    ) -> ResultPending:
        target = ResultPending(current.attempt, payload, idempotency_key)
        self._commit(current, target)
        return target

    def queue_outcome(
        self,
        current: Claimed | Launched | RenewIntent,
        outcome: TerminalOutcome,
        code: str,
        idempotency_key: str,
    ) -> OutcomePending:
        target = OutcomePending(current.attempt, outcome, code, idempotency_key)
        self._commit(current, target)
        return target

    def complete(self, current: ResultPending | OutcomePending) -> None:
        self._commit(current, None)

    def reject_outcome(
        self,
        current: OutcomePending,
        status_code: int | None,
    ) -> OutcomeRejected:
        target = OutcomeRejected(
            current.attempt,
            current.outcome,
            current.code,
            current.idempotency_key,
            status_code,
        )
        self._commit(current, target)
        return target
