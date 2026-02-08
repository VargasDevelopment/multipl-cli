from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from jsonschema import Draft7Validator

REPORT_VERSION = "acceptance.v1"
MAX_REASON_CHARS = 240
MAX_LIST_ITEMS = 20
MAX_TOP_LEVEL_KEYS = 50


@dataclass
class AcceptanceReport:
    version: str
    status: str
    checks: list[dict[str, Any]]
    stats: dict[str, Any]
    commitment: dict[str, Any]


class AcceptanceError(RuntimeError):
    pass


def _to_bounded_reason(value: str) -> str:
    return value if len(value) <= MAX_REASON_CHARS else f"{value[: MAX_REASON_CHARS - 3]}..."


def _to_bounded_list(entries: list[str]) -> list[str]:
    return entries[:MAX_LIST_ITEMS]


def _safe_top_level_keys(payload: Any) -> list[str] | None:
    if not isinstance(payload, dict):
        return None
    keys = list(payload.keys())[:MAX_TOP_LEVEL_KEYS]
    return keys or None


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_bytes(canonical: str) -> int:
    return len(canonical.encode("utf-8"))


def canonical_sha256(canonical: str) -> str:
    return sha256(canonical.encode("utf-8")).hexdigest()


def _path_exists(value: Any, path: str) -> bool:
    parts = [part.strip() for part in path.split(".") if part.strip()]
    if not parts:
        return False
    current = value
    for segment in parts:
        if isinstance(current, list):
            try:
                index = int(segment)
            except ValueError:
                return False
            if index < 0 or index >= len(current):
                return False
            current = current[index]
            continue
        if not isinstance(current, dict):
            return False
        if segment not in current:
            return False
        current = current[segment]
    return True


def _check_is_object(payload: Any) -> dict[str, Any]:
    passed = isinstance(payload, dict)
    return {
        "name": "deterministic:isObject",
        "passed": passed,
        "reason": None if passed else "payload must be a JSON object",
    }


def _check_no_nulls_top_level(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "name": "deterministic:noNullsTopLevel",
            "passed": False,
            "reason": "payload must be a JSON object",
        }
    null_keys = [key for key, value in payload.items() if value is None]
    return {
        "name": "deterministic:noNullsTopLevel",
        "passed": len(null_keys) == 0,
        "reason": None if len(null_keys) == 0 else "payload contains top-level null values",
        "details": {"nullKeys": null_keys} if null_keys else None,
    }


def _check_has_keys(payload: Any, check_name: str) -> dict[str, Any]:
    _, raw_keys = check_name.split(":", 1)
    keys = [entry.strip() for entry in raw_keys.split(",") if entry.strip()]
    if not isinstance(payload, dict):
        return {
            "name": f"deterministic:{check_name}",
            "passed": False,
            "reason": "payload must be a JSON object",
        }
    missing = [key for key in keys if key not in payload]
    return {
        "name": f"deterministic:{check_name}",
        "passed": len(missing) == 0,
        "reason": None if len(missing) == 0 else "payload is missing required top-level keys",
        "details": {"missingKeys": missing} if missing else None,
    }


def _run_deterministic(check_name: str, payload: Any) -> dict[str, Any]:
    if check_name == "isObject":
        return _check_is_object(payload)
    if check_name == "noNullsTopLevel":
        return _check_no_nulls_top_level(payload)
    if check_name.startswith("hasKeys:"):
        return _check_has_keys(payload, check_name)
    return {
        "name": f"deterministic:{check_name}",
        "passed": False,
        "reason": f"unsupported deterministic check \"{check_name}\"",
    }


def _summarize_schema_errors(errors: list[str]) -> str:
    if not errors:
        return "output does not match schema"
    return _to_bounded_reason("; ".join(errors[:3]))


def validate_acceptance(acceptance_contract: Any, payload: Any) -> AcceptanceReport:
    canonical = canonical_json(payload)
    canonical_size = canonical_bytes(canonical)
    sha = canonical_sha256(canonical)

    def report(status: str, checks: list[dict[str, Any]]) -> AcceptanceReport:
        computed_at = datetime.now(timezone.utc).isoformat()
        return AcceptanceReport(
            version=REPORT_VERSION,
            status=status,
            checks=checks,
            stats={"bytes": canonical_size, "topLevelKeys": _safe_top_level_keys(payload)},
            commitment={"sha256": sha, "computedAt": computed_at},
        )

    if acceptance_contract is None or acceptance_contract == {}:
        return report("skipped", [{"name": "acceptance", "passed": True, "reason": "acceptance contract missing"}])

    if not isinstance(acceptance_contract, dict):
        return report(
            "error",
            [
                {
                    "name": "contract",
                    "passed": False,
                    "reason": "invalid acceptance contract: must be object",
                }
            ],
        )

    contract = acceptance_contract
    normalized_empty = (
        contract.get("maxBytes") is None
        and contract.get("outputSchema") is None
        and not (contract.get("mustInclude") or {}).get("keys")
        and not (contract.get("mustInclude") or {}).get("substrings")
        and not contract.get("deterministicChecks")
    )
    if normalized_empty:
        return report("skipped", [{"name": "acceptance", "passed": True, "reason": "acceptance contract missing"}])
    checks: list[dict[str, Any]] = []

    max_bytes = contract.get("maxBytes")
    if isinstance(max_bytes, int):
        passed = canonical_size <= max_bytes
        checks.append(
            {
                "name": "maxBytes",
                "passed": passed,
                "reason": None
                if passed
                else f"canonical payload is {canonical_size} bytes (limit {max_bytes})",
                "details": None
                if passed
                else {"actualBytes": canonical_size, "maxBytes": max_bytes},
            }
        )

    must_include = contract.get("mustInclude") if isinstance(contract.get("mustInclude"), dict) else {}
    keys = must_include.get("keys") if isinstance(must_include.get("keys"), list) else []
    if keys:
        missing_keys = [key for key in keys if isinstance(key, str) and not _path_exists(payload, key)]
        checks.append(
            {
                "name": "mustInclude.keys",
                "passed": len(missing_keys) == 0,
                "reason": None if len(missing_keys) == 0 else "payload is missing required keys",
                "details": None
                if len(missing_keys) == 0
                else {"missingKeys": _to_bounded_list(missing_keys), "totalMissing": len(missing_keys)},
            }
        )

    substrings = must_include.get("substrings") if isinstance(must_include.get("substrings"), list) else []
    if substrings:
        missing_substrings = [
            value for value in substrings if isinstance(value, str) and value not in canonical
        ]
        checks.append(
            {
                "name": "mustInclude.substrings",
                "passed": len(missing_substrings) == 0,
                "reason": None
                if len(missing_substrings) == 0
                else "canonical payload string is missing required substrings",
                "details": None
                if len(missing_substrings) == 0
                else {
                    "missingSubstrings": _to_bounded_list(missing_substrings),
                    "totalMissing": len(missing_substrings),
                },
            }
        )

    output_schema = contract.get("outputSchema")
    if isinstance(output_schema, dict):
        try:
            validator = Draft7Validator(output_schema)
            errors = [
                f"{error.json_path or '/'} {error.message}"
                for error in validator.iter_errors(payload)
            ]
            valid = not errors
            checks.append(
                {
                    "name": "schema",
                    "passed": valid,
                    "reason": None if valid else _summarize_schema_errors(errors),
                }
            )
        except Exception as exc:
            checks.append({"name": "schema", "passed": False, "reason": str(exc)})
            return report("error", checks)

    deterministic = contract.get("deterministicChecks")
    if isinstance(deterministic, list):
        for check in deterministic:
            if not isinstance(check, str):
                continue
            checks.append(_run_deterministic(check, payload))

    failed = [check for check in checks if not check.get("passed")]
    return report("fail" if failed else "pass", checks)
