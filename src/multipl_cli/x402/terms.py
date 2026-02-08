from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class PaymentTerms:
    recipient: str
    amount: int
    asset: str
    network: str
    payment_context: str
    facilitator: str | None = None
    hint: str | None = None
    preview_json: Any | None = None
    commitment_sha256: str | None = None
    acceptance_report: Any | None = None
    metadata: dict[str, Any] | None = None


class PaymentTermsError(RuntimeError):
    pass


def parse_payment_terms(response: httpx.Response) -> PaymentTerms:
    try:
        payload = response.json()
    except Exception as exc:
        raise PaymentTermsError("payment_required response is not JSON") from exc
    if not isinstance(payload, dict):
        raise PaymentTermsError("payment_required response is not an object")

    required = ["recipient", "amount", "asset", "network", "payment_context"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise PaymentTermsError(f"missing payment fields: {', '.join(missing)}")

    recipient = str(payload["recipient"])
    amount_value = payload["amount"]
    try:
        amount = int(amount_value)
    except Exception as exc:
        raise PaymentTermsError("amount is not an integer") from exc

    return PaymentTerms(
        recipient=recipient,
        amount=amount,
        asset=str(payload["asset"]),
        network=str(payload["network"]),
        payment_context=str(payload["payment_context"]),
        facilitator=payload.get("facilitator"),
        hint=payload.get("hint"),
        preview_json=payload.get("previewJson"),
        commitment_sha256=payload.get("commitmentSha256"),
        acceptance_report=payload.get("acceptanceReport"),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
    )
