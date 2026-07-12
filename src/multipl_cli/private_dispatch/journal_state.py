from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal, TypeAlias

from multipl_cli.private_dispatch.types import (
    TERMINAL_CODES,
    Attempt,
    Lease,
    ProcessIdentity,
    TaskIdentity,
)

TerminalOutcome: TypeAlias = Literal["failed", "unknown"]


class JournalCodecError(ValueError):
    """The on-disk dispatcher journal is not a recognized state record."""


@dataclass(frozen=True)
class TerminalDirective:
    outcome: TerminalOutcome
    code: str


@dataclass(frozen=True)
class AcquireIntent:
    allowlist: tuple[TaskIdentity, ...]
    idempotency_key: str
    state: Literal["acquire_intent"] = field(default="acquire_intent", init=False)


@dataclass(frozen=True)
class AcquireResponse:
    allowlist: tuple[TaskIdentity, ...]
    idempotency_key: str
    attempt: Attempt | None
    state: Literal["acquire_response"] = field(default="acquire_response", init=False)


@dataclass(frozen=True)
class Claimed:
    attempt: Attempt
    state: Literal["claimed"] = field(default="claimed", init=False)


@dataclass(frozen=True)
class Launched:
    """A launch intent, optionally enriched with the durable process identity."""

    attempt: Attempt
    task_key: str
    process: ProcessIdentity | None = None
    state: Literal["launched"] = field(default="launched", init=False)


@dataclass(frozen=True)
class RenewIntent:
    attempt: Attempt
    task_key: str
    idempotency_key: str
    process: ProcessIdentity | None = None
    terminal: TerminalDirective | None = None
    state: Literal["renew_intent"] = field(default="renew_intent", init=False)


@dataclass(frozen=True)
class ResultPending:
    attempt: Attempt
    payload: object
    idempotency_key: str
    state: Literal["result_pending"] = field(default="result_pending", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", _json_value(self.payload))


@dataclass(frozen=True)
class OutcomePending:
    attempt: Attempt
    outcome: TerminalOutcome
    code: str
    idempotency_key: str
    state: Literal["outcome_pending"] = field(default="outcome_pending", init=False)


@dataclass(frozen=True)
class OutcomeRejected:
    """A definitive terminal API rejection that must not be replayed blindly."""

    attempt: Attempt
    outcome: TerminalOutcome
    code: str
    idempotency_key: str
    status_code: int | None
    state: Literal["outcome_rejected"] = field(default="outcome_rejected", init=False)


JournalState: TypeAlias = (
    AcquireIntent
    | AcquireResponse
    | Claimed
    | Launched
    | RenewIntent
    | ResultPending
    | OutcomePending
    | OutcomeRejected
)


def _object(value: object, label: str, fields: frozenset[str]) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise JournalCodecError(f"{label} must be an object")
    actual = frozenset(value)
    if actual != fields:
        missing = sorted(fields - actual)
        extra = sorted(actual - fields)
        raise JournalCodecError(f"{label} fields are invalid (missing={missing}, extra={extra})")
    return value


def _variant(
    value: object,
    label: str,
    state: str,
    fields: frozenset[str],
) -> dict[str, object]:
    data = _object(value, label, fields)
    if data["state"] != state:
        raise JournalCodecError(f"{label} has the wrong discriminator")
    return data


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise JournalCodecError(f"{label} must be a non-empty string")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise JournalCodecError(f"{label} must be a positive integer")
    return value


def _status_code(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not 100 <= value <= 599:
        raise JournalCodecError("journal rejection statusCode is invalid")
    return value


def _identity(value: object) -> TaskIdentity:
    data = _object(value, "journal identity", frozenset({"registryId", "typeId", "version"}))
    return TaskIdentity(
        _text(data["registryId"], "journal identity registryId"),
        _text(data["typeId"], "journal identity typeId"),
        _positive_int(data["version"], "journal identity version"),
    )


def _allowlist(value: object) -> tuple[TaskIdentity, ...]:
    if not isinstance(value, list) or not value:
        raise JournalCodecError("journal allowlist must be a non-empty array")
    return tuple(_identity(item) for item in value)


def _lease(value: object) -> Lease:
    data = _object(value, "journal lease", frozenset({"leaseId", "generation", "expiresAt"}))
    return Lease(
        _text(data["leaseId"], "journal leaseId"),
        _positive_int(data["generation"], "journal lease generation"),
        _text(data["expiresAt"], "journal lease expiresAt"),
    )


def _attempt(value: object) -> Attempt:
    data = _object(value, "journal attempt", frozenset({"attemptId", "workId", "lease"}))
    return Attempt(
        _text(data["attemptId"], "journal attemptId"),
        _text(data["workId"], "journal workId"),
        _lease(data["lease"]),
    )


def _process(value: object) -> ProcessIdentity | None:
    if value is None:
        return None
    data = _object(
        value,
        "journal process",
        frozenset({"pid", "pgid", "startTime", "commandHash"}),
    )
    pid = _positive_int(data["pid"], "journal process pid")
    pgid = _positive_int(data["pgid"], "journal process pgid")
    start_time = data["startTime"]
    command_hash = _text(data["commandHash"], "journal process commandHash")
    if (
        pid <= 1
        or pgid <= 1
        or isinstance(start_time, bool)
        or not isinstance(start_time, int)
        or start_time < 0
        or len(command_hash) != 64
        or any(character not in "0123456789abcdef" for character in command_hash)
    ):
        raise JournalCodecError("journal process identity is invalid")
    return ProcessIdentity(pid, pgid, start_time, command_hash)


def _terminal(value: object) -> TerminalDirective | None:
    if value is None:
        return None
    data = _object(value, "journal terminal", frozenset({"outcome", "code"}))
    outcome = data["outcome"]
    code = data["code"]
    if (
        not isinstance(outcome, str)
        or outcome not in {"failed", "unknown"}
        or not isinstance(code, str)
        or code not in TERMINAL_CODES
    ):
        raise JournalCodecError("journal terminal directive is invalid")
    return TerminalDirective(outcome, code)


def _json_value(value: object, label: str = "journal payload", *, mutable: bool = False) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise JournalCodecError(f"{label} contains a non-finite number")
        return value
    if isinstance(value, list) or (mutable and isinstance(value, tuple)):
        items = [_json_value(item, label, mutable=mutable) for item in value]
        return items if mutable else tuple(items)
    if (
        (isinstance(value, dict) or (mutable and isinstance(value, Mapping)))
        and all(isinstance(key, str) for key in value)
    ):
        items = {key: _json_value(item, label, mutable=mutable) for key, item in value.items()}
        return items if mutable else MappingProxyType(items)
    raise JournalCodecError(f"{label} is not JSON-compatible")


def json_for_submission(value: object) -> object:
    return _json_value(value, mutable=True)


def _terminal_fields(value: dict[str, object], label: str) -> tuple[TerminalOutcome, str]:
    outcome = value["outcome"]
    code = value["code"]
    if (
        not isinstance(outcome, str)
        or outcome not in {"failed", "unknown"}
        or not isinstance(code, str)
        or code not in TERMINAL_CODES
    ):
        raise JournalCodecError(f"{label} terminal fields are invalid")
    return outcome, code


def _decode_acquire_intent(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "acquire_intent",
        "acquire_intent",
        frozenset({"state", "allowlist", "idempotencyKey"}),
    )
    return AcquireIntent(
        _allowlist(value["allowlist"]), _text(value["idempotencyKey"], "idempotencyKey")
    )


def _decode_acquire_response(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "acquire_response",
        "acquire_response",
        frozenset({"state", "allowlist", "idempotencyKey", "attempt"}),
    )
    raw_attempt = value["attempt"]
    return AcquireResponse(
        _allowlist(value["allowlist"]),
        _text(value["idempotencyKey"], "idempotencyKey"),
        None if raw_attempt is None else _attempt(raw_attempt),
    )


def _decode_claimed(data: dict[str, object]) -> JournalState:
    value = _variant(data, "claimed", "claimed", frozenset({"state", "attempt"}))
    return Claimed(_attempt(value["attempt"]))


def _decode_launched(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "launched",
        "launched",
        frozenset({"state", "attempt", "taskKey", "process"}),
    )
    return Launched(
        _attempt(value["attempt"]),
        _text(value["taskKey"], "taskKey"),
        _process(value["process"]),
    )


def _decode_renew_intent(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "renew_intent",
        "renew_intent",
        frozenset({"state", "attempt", "taskKey", "idempotencyKey", "process", "terminal"}),
    )
    return RenewIntent(
        _attempt(value["attempt"]),
        _text(value["taskKey"], "taskKey"),
        _text(value["idempotencyKey"], "idempotencyKey"),
        _process(value["process"]),
        _terminal(value["terminal"]),
    )


def _decode_result_pending(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "result_pending",
        "result_pending",
        frozenset({"state", "attempt", "payload", "idempotencyKey"}),
    )
    return ResultPending(
        _attempt(value["attempt"]),
        value["payload"],
        _text(value["idempotencyKey"], "idempotencyKey"),
    )


def _decode_outcome_pending(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "outcome_pending",
        "outcome_pending",
        frozenset({"state", "attempt", "outcome", "code", "idempotencyKey"}),
    )
    outcome, code = _terminal_fields(value, "outcome_pending")
    return OutcomePending(
        _attempt(value["attempt"]),
        outcome,
        code,
        _text(value["idempotencyKey"], "idempotencyKey"),
    )


def _decode_outcome_rejected(data: dict[str, object]) -> JournalState:
    value = _variant(
        data,
        "outcome_rejected",
        "outcome_rejected",
        frozenset({"state", "attempt", "outcome", "code", "idempotencyKey", "statusCode"}),
    )
    outcome, code = _terminal_fields(value, "outcome_rejected")
    return OutcomeRejected(
        _attempt(value["attempt"]),
        outcome,
        code,
        _text(value["idempotencyKey"], "idempotencyKey"),
        _status_code(value["statusCode"]),
    )


_DECODERS: dict[str, Callable[[dict[str, object]], JournalState]] = {
    "acquire_intent": _decode_acquire_intent,
    "acquire_response": _decode_acquire_response,
    "claimed": _decode_claimed,
    "launched": _decode_launched,
    "renew_intent": _decode_renew_intent,
    "result_pending": _decode_result_pending,
    "outcome_pending": _decode_outcome_pending,
    "outcome_rejected": _decode_outcome_rejected,
}


def _encode_identity(identity: TaskIdentity) -> dict[str, object]:
    return {
        "registryId": identity.registry_id,
        "typeId": identity.type_id,
        "version": identity.version,
    }


def _encode_attempt(attempt: Attempt) -> dict[str, object]:
    return {
        "attemptId": attempt.attempt_id,
        "workId": attempt.work_id,
        "lease": {
            "leaseId": attempt.lease.lease_id,
            "generation": attempt.lease.generation,
            "expiresAt": attempt.lease.expires_at,
        },
    }


def _encode_process(process: ProcessIdentity | None) -> dict[str, object] | None:
    if process is None:
        return None
    return {
        "pid": process.pid,
        "pgid": process.pgid,
        "startTime": process.start_time,
        "commandHash": process.command_hash,
    }


def _encode_terminal(terminal: TerminalDirective | None) -> dict[str, object] | None:
    if terminal is None:
        return None
    return {"outcome": terminal.outcome, "code": terminal.code}


def _encode_state(state: JournalState) -> dict[str, object]:
    if isinstance(state, AcquireIntent):
        return {
            "state": state.state,
            "allowlist": [_encode_identity(item) for item in state.allowlist],
            "idempotencyKey": state.idempotency_key,
        }
    if isinstance(state, AcquireResponse):
        return {
            "state": state.state,
            "allowlist": [_encode_identity(item) for item in state.allowlist],
            "idempotencyKey": state.idempotency_key,
            "attempt": None if state.attempt is None else _encode_attempt(state.attempt),
        }
    if isinstance(state, Claimed):
        return {"state": state.state, "attempt": _encode_attempt(state.attempt)}
    if isinstance(state, Launched):
        return {
            "state": state.state,
            "attempt": _encode_attempt(state.attempt),
            "taskKey": state.task_key,
            "process": _encode_process(state.process),
        }
    if isinstance(state, RenewIntent):
        return {
            "state": state.state,
            "attempt": _encode_attempt(state.attempt),
            "taskKey": state.task_key,
            "idempotencyKey": state.idempotency_key,
            "process": _encode_process(state.process),
            "terminal": _encode_terminal(state.terminal),
        }
    if isinstance(state, ResultPending):
        return {
            "state": state.state,
            "attempt": _encode_attempt(state.attempt),
            "payload": json_for_submission(state.payload),
            "idempotencyKey": state.idempotency_key,
        }
    if isinstance(state, OutcomePending):
        return {
            "state": state.state,
            "attempt": _encode_attempt(state.attempt),
            "outcome": state.outcome,
            "code": state.code,
            "idempotencyKey": state.idempotency_key,
        }
    if isinstance(state, OutcomeRejected):
        return {
            "state": state.state,
            "attempt": _encode_attempt(state.attempt),
            "outcome": state.outcome,
            "code": state.code,
            "idempotencyKey": state.idempotency_key,
            "statusCode": state.status_code,
        }
    raise JournalCodecError(f"unsupported dispatcher journal state: {type(state).__name__}")


def decode_state(value: object) -> JournalState:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise JournalCodecError("dispatcher journal must be an object")
    discriminator = value.get("state")
    if not isinstance(discriminator, str) or discriminator not in _DECODERS:
        raise JournalCodecError("dispatcher journal state is unknown")
    return _DECODERS[discriminator](value)


def encode_state(state: JournalState) -> dict[str, object]:
    try:
        encoded = _encode_state(state)
        decode_state(encoded)
    except (AttributeError, KeyError, RecursionError, TypeError, ValueError) as exc:
        if isinstance(exc, JournalCodecError):
            raise
        raise JournalCodecError("dispatcher journal state is invalid") from exc
    return encoded


def serialize_state(state: JournalState) -> bytes:
    try:
        return json.dumps(
            encode_state(state),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (JournalCodecError, RecursionError, TypeError, ValueError) as exc:
        if isinstance(exc, JournalCodecError):
            raise
        raise JournalCodecError("dispatcher journal cannot be serialized") from exc


def parse_state(content: bytes) -> JournalState:
    def reject_constant(_value: str) -> None:
        raise JournalCodecError("dispatcher journal contains a non-finite number")

    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise JournalCodecError("dispatcher journal contains a duplicate field")
            value[key] = item
        return value

    try:
        value = json.loads(
            content,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
        )
    except (RecursionError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise JournalCodecError("dispatcher journal is not valid JSON") from exc
    return decode_state(value)
