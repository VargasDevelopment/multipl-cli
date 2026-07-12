from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from multipl_cli.private_dispatch.journal_state import (
    AcquireIntent,
    AcquireResponse,
    Claimed,
    JournalCodecError,
    Launched,
    OutcomePending,
    OutcomeRejected,
    RenewIntent,
    ResultPending,
    TerminalDirective,
    decode_state,
    encode_state,
    json_for_submission,
    parse_state,
    serialize_state,
)
from multipl_cli.private_dispatch.state_machine import (
    LEGAL_TRANSITIONS,
    IllegalJournalTransition,
    JournalStateMachine,
    dispatch_recovery,
    transition_allowed,
    validate_transition,
)
from multipl_cli.private_dispatch.storage import Journal
from multipl_cli.private_dispatch.types import Attempt, Lease, ProcessIdentity, TaskIdentity

IDENTITY = TaskIdentity("registry.id", "document.index", 1)
ATTEMPT = Attempt("attempt-1", "work-1", Lease("lease-1", 2, "2030-01-01T00:00:00Z"))
PROCESS = ProcessIdentity(1234, 1234, 5678, "a" * 64)


def _states() -> tuple[object, ...]:
    return (
        AcquireIntent((IDENTITY,), "acquire-key"),
        AcquireResponse((IDENTITY,), "acquire-key", ATTEMPT),
        Claimed(ATTEMPT),
        Launched(ATTEMPT, IDENTITY.key, PROCESS),
        RenewIntent(
            ATTEMPT,
            IDENTITY.key,
            "renew-key",
            PROCESS,
            TerminalDirective("failed", "renew_ambiguous"),
        ),
        ResultPending(ATTEMPT, {"result": [1, True, None]}, "result-key"),
        OutcomePending(ATTEMPT, "unknown", "lease_lost", "outcome-key"),
        OutcomeRejected(ATTEMPT, "unknown", "lease_lost", "outcome-key", 404),
    )


@pytest.mark.parametrize("state", _states(), ids=lambda state: state.state)
def test_every_journal_variant_round_trips_through_one_codec(state: object) -> None:
    encoded = encode_state(state)  # type: ignore[arg-type]

    assert decode_state(encoded) == state
    assert parse_state(serialize_state(state)) == state  # type: ignore[arg-type]


@pytest.mark.parametrize("state", _states(), ids=lambda state: state.state)
def test_every_journal_variant_rejects_unknown_fields(state: object) -> None:
    encoded = encode_state(state)  # type: ignore[arg-type]
    encoded["unexpected"] = True

    with pytest.raises(JournalCodecError):
        decode_state(encoded)


@pytest.mark.parametrize("state", _states(), ids=lambda state: state.state)
def test_encode_output_is_detached_for_every_journal_variant(state: object) -> None:
    expected = encode_state(state)
    encoded = encode_state(state)
    encoded["state"] = "mutated"
    if "allowlist" in encoded:
        encoded["allowlist"][0]["version"] = 99
    else:
        encoded["attempt"]["lease"]["generation"] = 99

    assert encode_state(state) == expected


def test_result_payload_is_deeply_immutable_across_boundaries() -> None:
    source = {"nested": {"rows": [{"values": [1, {"ok": True}]}]}}
    expected = {"nested": {"rows": [{"values": [1, {"ok": True}]}]}}
    state = ResultPending(ATTEMPT, source, "result-key")
    source["nested"]["rows"][0]["values"][1]["ok"] = False
    source["nested"]["rows"].append({"values": []})

    encoded = encode_state(state)
    decoded = decode_state(encoded)
    encoded["payload"]["nested"]["rows"][0]["values"].append("encoded")
    submission = json_for_submission(decoded.payload)
    submission["nested"]["rows"][0]["values"].append("submitted")

    assert encode_state(state)["payload"] == expected
    assert encode_state(decoded)["payload"] == expected


def test_queue_result_freezes_payload_owned_by_reducer(tmp_path: Path) -> None:
    journal = Journal(tmp_path / "state")
    launched = Launched(ATTEMPT, IDENTITY.key)
    journal.write(launched)
    machine = JournalStateMachine(journal)
    source = {"nested": [{"items": [1, 2]}]}
    pending = machine.queue_result(launched, source, "result-key")
    source["nested"][0]["items"].append(3)

    assert encode_state(pending)["payload"] == {"nested": [{"items": [1, 2]}]}


def test_codec_rejects_missing_fields_wrong_types_and_non_finite_numbers() -> None:
    claimed = encode_state(Claimed(ATTEMPT))
    del claimed["attempt"]
    with pytest.raises(JournalCodecError):
        decode_state(claimed)

    corrupt = encode_state(Claimed(ATTEMPT))
    corrupt["attempt"] = {
        "attemptId": ATTEMPT.attempt_id,
        "workId": ATTEMPT.work_id,
        "lease": {
            "leaseId": ATTEMPT.lease.lease_id,
            "generation": True,
            "expiresAt": ATTEMPT.lease.expires_at,
        },
    }
    with pytest.raises(JournalCodecError):
        decode_state(corrupt)

    with pytest.raises(JournalCodecError):
        parse_state(b'{"state":"result_pending","payload":NaN}')

    with pytest.raises(JournalCodecError):
        parse_state(b'{"state":"claimed","state":"claimed","attempt":null}')

    with pytest.raises(JournalCodecError):
        decode_state({"state": "not_a_state"})


def test_journal_only_writes_frozen_variants_and_rejects_raw_records(tmp_path: Path) -> None:
    journal = Journal(tmp_path / "state")
    journal.write(Claimed(ATTEMPT))
    assert journal.load() == Claimed(ATTEMPT)

    with pytest.raises(JournalCodecError):
        journal.write({"state": "claimed"})  # type: ignore[arg-type]

    loaded = journal.load()
    assert loaded is not None
    with pytest.raises(FrozenInstanceError):
        loaded.attempt = ATTEMPT  # type: ignore[misc]


def test_journal_load_rejects_corrupt_bytes(tmp_path: Path) -> None:
    journal = Journal(tmp_path / "state")
    journal.path.parent.mkdir()
    journal.path.write_bytes(b'{"state":"claimed","attempt":null}')

    with pytest.raises(JournalCodecError):
        journal.load()


def test_transition_table_covers_every_legal_and_illegal_pair() -> None:
    states = _states()
    samples = {type(state): state for state in states}
    samples[type(None)] = None
    state_types = tuple(samples)

    for current_type in state_types:
        current = samples[current_type]
        allowed = LEGAL_TRANSITIONS.get(current_type, frozenset())
        for target_type in state_types:
            target = samples[target_type]
            assert transition_allowed(current, target) is (target_type in allowed)
            if target_type in allowed:
                validate_transition(current, target)
            else:
                with pytest.raises(IllegalJournalTransition):
                    validate_transition(current, target)


class _RecoveryRecorder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def recover_ready(self) -> str:
        self.calls.append("ready")
        return "ready"

    def _state(self, state: object) -> str:
        self.calls.append(state.state)
        return state.state

    def recover_acquire_intent(self, state: AcquireIntent) -> str:
        return self._state(state)

    def recover_acquire_response(self, state: AcquireResponse) -> str:
        return self._state(state)

    def recover_claimed(self, state: Claimed) -> str:
        return self._state(state)

    def recover_launched(self, state: Launched) -> str:
        return self._state(state)

    def recover_renew_intent(self, state: RenewIntent) -> str:
        return self._state(state)

    def recover_result_pending(self, state: ResultPending) -> str:
        return self._state(state)

    def recover_outcome_pending(self, state: OutcomePending) -> str:
        return self._state(state)

    def recover_outcome_rejected(self, state: OutcomeRejected) -> str:
        return self._state(state)


@pytest.mark.parametrize(
    "state", (None, *_states()), ids=lambda state: "ready" if state is None else state.state
)
def test_restart_recovery_dispatch_has_one_typed_route_per_state(state: object) -> None:
    handler = _RecoveryRecorder()

    result = dispatch_recovery(state, handler)  # type: ignore[arg-type]

    expected = "ready" if state is None else state.state
    assert result == expected
    assert handler.calls == [expected]
