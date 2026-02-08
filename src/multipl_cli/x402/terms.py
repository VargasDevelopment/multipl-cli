from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from x402.http import PAYMENT_REQUIRED_HEADER, decode_payment_required_header
from x402.schemas import PaymentRequired, PaymentRequirements


@dataclass
class PaymentTerms:
    payment_required: PaymentRequired
    requirement: PaymentRequirements
    recipient: str
    amount: int | str
    asset: str
    network: str
    payment_context: str | None
    facilitator: str | None = None
    hint: str | None = None
    preview_json: Any | None = None
    commitment_sha256: str | None = None
    acceptance_report: Any | None = None
    metadata: dict[str, Any] | None = None


class PaymentTermsError(RuntimeError):
    pass


def _extract_payment_context(payment_required: PaymentRequired, payload: dict[str, Any]) -> str | None:
    value = payload.get("payment_context")
    if isinstance(value, str):
        return value
    extensions = payment_required.extensions or {}
    multipl = extensions.get("multipl") if isinstance(extensions, dict) else None
    info = multipl.get("info") if isinstance(multipl, dict) else None
    if isinstance(info, dict):
        ext_value = info.get("payment_context") or info.get("paymentContext")
        if isinstance(ext_value, str):
            return ext_value
    return None


def _select_requirement(payment_required: PaymentRequired) -> PaymentRequirements:
    for requirement in payment_required.accepts:
        if requirement.scheme == "exact":
            return requirement
    return payment_required.accepts[0]


def parse_payment_terms(response: httpx.Response) -> PaymentTerms:
    header_value = response.headers.get(PAYMENT_REQUIRED_HEADER) or response.headers.get(
        PAYMENT_REQUIRED_HEADER.lower()
    )
    if not header_value:
        raise PaymentTermsError("PAYMENT-REQUIRED header missing from 402 response")

    try:
        payment_required = decode_payment_required_header(header_value)
    except Exception as exc:
        raise PaymentTermsError("PAYMENT-REQUIRED header is invalid") from exc

    if not isinstance(payment_required, PaymentRequired):
        raise PaymentTermsError("unsupported x402 version")
    if not payment_required.accepts:
        raise PaymentTermsError("PAYMENT-REQUIRED missing accepted requirements")

    try:
        payload = response.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    requirement = _select_requirement(payment_required)
    payment_context = _extract_payment_context(payment_required, payload)

    recipient = str(payload.get("recipient") or requirement.pay_to)
    amount_value = payload.get("amount")
    if isinstance(amount_value, (int, float)):
        amount: int | str = int(amount_value)
    else:
        amount = requirement.amount

    asset = str(payload.get("asset") or requirement.asset)
    network = str(payload.get("network") or requirement.network)

    return PaymentTerms(
        payment_required=payment_required,
        requirement=requirement,
        recipient=recipient,
        amount=amount,
        asset=asset,
        network=network,
        payment_context=payment_context,
        facilitator=payload.get("facilitator"),
        hint=payload.get("hint"),
        preview_json=payload.get("previewJson"),
        commitment_sha256=payload.get("commitmentSha256"),
        acceptance_report=payload.get("acceptanceReport"),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
    )
