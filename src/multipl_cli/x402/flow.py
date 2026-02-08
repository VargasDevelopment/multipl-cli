from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import httpx
from x402.http import PAYMENT_SIGNATURE_HEADER

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.proof import ProofCache, cache_key_from_terms, proof_to_header_value
from multipl_cli.x402.terms import PaymentTerms, PaymentTermsError, parse_payment_terms


@dataclass
class PaymentRequiredError(RuntimeError):
    terms: PaymentTerms


class PaymentFlowError(RuntimeError):
    pass


def _terms_cache_id(terms: PaymentTerms) -> dict:
    return {
        "payTo": terms.requirement.pay_to,
        "amount": terms.requirement.amount,
        "asset": terms.requirement.asset,
        "network": str(terms.requirement.network),
        "payment_context": terms.payment_context,
    }


def request_with_x402(
    request_fn: Callable[[dict[str, str] | None], httpx.Response],
    *,
    payer: Payer,
    allow_pay: bool,
    proof_cache: ProofCache | None = None,
) -> httpx.Response:
    response = request_fn(None)
    if response.status_code != 402:
        return response

    try:
        terms = parse_payment_terms(response)
    except PaymentTermsError as exc:
        raise PaymentFlowError(str(exc)) from exc

    if not allow_pay:
        raise PaymentRequiredError(terms)

    cache = proof_cache or ProofCache.load()
    cache_id = _terms_cache_id(terms)
    cache_key = cache_key_from_terms(cache_id)
    def build_headers(proof: dict) -> dict[str, str]:
        headers = {
            PAYMENT_SIGNATURE_HEADER: proof_to_header_value(proof),
        }
        if terms.payment_context:
            headers["x-payment-context"] = terms.payment_context
        return headers

    def is_receipt_replay(resp: httpx.Response) -> bool:
        if resp.status_code != 409:
            return False
        try:
            payload = resp.json()
        except Exception:
            return False
        return isinstance(payload, dict) and payload.get("error") == "receipt_replay"

    def is_proof_rejected(resp: httpx.Response) -> bool:
        if resp.status_code == 402:
            return True
        if resp.status_code == 422:
            try:
                payload = resp.json()
            except Exception:
                return False
            return isinstance(payload, dict) and payload.get("error") == "invalid_payment_proof"
        return False

    def get_proof(force_refresh: bool) -> dict:
        proof = None if force_refresh else cache.get(cache_key)
        if proof is None:
            try:
                proof = payer.get_proof(terms)
            except PayerError as exc:
                raise PaymentFlowError(str(exc)) from exc
            cache.set(cache_key, proof)
            cache.save()
        return proof

    regenerated = False
    proof = get_proof(force_refresh=False)
    paid_response = request_fn(build_headers(proof))

    if (is_receipt_replay(paid_response) or is_proof_rejected(paid_response)) and not regenerated:
        cache.delete(cache_key)
        cache.save()
        regenerated = True
        proof = get_proof(force_refresh=True)
        paid_response = request_fn(build_headers(proof))

    return paid_response
