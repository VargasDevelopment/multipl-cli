from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import httpx

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.proof import ProofCache, cache_key_from_terms, proof_to_header_value
from multipl_cli.x402.terms import PaymentTerms, PaymentTermsError, parse_payment_terms


@dataclass
class PaymentRequiredError(RuntimeError):
    terms: PaymentTerms


class PaymentFlowError(RuntimeError):
    pass


def _terms_cache_id(terms: PaymentTerms) -> dict:
    metadata = terms.metadata or {}
    return {
        "jobId": metadata.get("jobId"),
        "recipient": terms.recipient,
        "amount": terms.amount,
        "asset": terms.asset,
        "network": terms.network,
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
    proof = cache.get(cache_key)

    if proof is None:
        try:
            proof = payer.get_proof(terms)
        except PayerError as exc:
            raise PaymentFlowError(str(exc)) from exc
        cache.set(cache_key, proof)
        cache.save()

    headers = {
        "x-payment": proof_to_header_value(proof),
        "x-payment-context": terms.payment_context,
    }
    paid_response = request_fn(headers)

    if paid_response.status_code == 409:
        try:
            payload = paid_response.json()
        except Exception:
            payload = None
        if isinstance(payload, dict) and payload.get("error") == "receipt_replay":
            cache.delete(cache_key)
            cache.save()
            return request_fn(None)

    return paid_response
