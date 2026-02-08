from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any

from multipl_cli.config import config_dir

PROOF_CACHE_FILE = "x402_proofs.json"


class ProofError(RuntimeError):
    pass


def parse_proof_value(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProofError("payment proof is not valid JSON") from exc
    if not isinstance(data, dict):
        raise ProofError("payment proof must be a JSON object")
    return data


def load_proof_from_file(path: Path) -> dict[str, Any]:
    return parse_proof_value(path.read_text())


def _validate_proof_structure(proof: dict[str, Any]) -> None:
    has_payload = isinstance(proof.get("paymentPayload"), dict)
    has_requirements = isinstance(proof.get("paymentRequirements"), dict)
    has_direct_payload = isinstance(proof.get("x402Version"), (int, float)) and isinstance(
        proof.get("accepted"), dict
    )
    if (has_payload and has_requirements) or has_direct_payload:
        return
    raise ProofError(
        "payment proof must include paymentPayload + paymentRequirements (or a direct "
        "x402 payload with accepted requirements)"
    )


def proof_to_header_value(proof: dict[str, Any]) -> str:
    if not isinstance(proof, dict):
        raise ProofError("payment proof must be a JSON object")
    _validate_proof_structure(proof)
    payload = json.dumps(proof, separators=(",", ":"), sort_keys=True)
    return base64.b64encode(payload.encode("utf-8")).decode("utf-8")


def cache_key_from_terms(terms_id: dict[str, Any]) -> str:
    payload = json.dumps(terms_id, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ProofCache:
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "ProofCache":
        path = config_dir() / PROOF_CACHE_FILE
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return cls()
        entries = data.get("entries")
        if not isinstance(entries, dict):
            return cls()
        return cls(entries=entries)

    def save(self) -> None:
        path = config_dir() / PROOF_CACHE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"entries": self.entries}
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self.entries.get(key)
        if isinstance(entry, dict):
            return entry.get("proof") if isinstance(entry.get("proof"), dict) else None
        return None

    def set(self, key: str, proof: dict[str, Any]) -> None:
        self.entries[key] = {"proof": proof}

    def delete(self, key: str) -> None:
        self.entries.pop(key, None)
