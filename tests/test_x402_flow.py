from __future__ import annotations

from dataclasses import dataclass

from x402.http import PAYMENT_REQUIRED_HEADER
from x402.http.utils import encode_payment_required_header
from x402.schemas import PaymentPayload, PaymentRequired, PaymentRequirements, ResourceInfo

from multipl_cli.x402.flow import request_with_x402
from multipl_cli.x402.payer_base import Payer
from multipl_cli.x402.proof import ProofCache
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class FakeResponse:
    status_code: int
    headers: dict[str, str] | None = None
    payload: dict | None = None

    def json(self) -> dict:
        if self.payload is None:
            raise ValueError("no json")
        return self.payload


class DummyPayer(Payer):
    name: str = "dummy"

    def __init__(self) -> None:
        self.calls = 0

    def get_proof(self, terms: PaymentTerms) -> dict:
        self.calls += 1
        payload = PaymentPayload(
            payload={"nonce": f"proof-{self.calls}"},
            accepted=terms.requirement,
            resource=terms.payment_required.resource,
            extensions=terms.payment_required.extensions,
        )
        return payload.model_dump(by_alias=True, exclude_none=True)


def _payment_required_header() -> str:
    requirements = PaymentRequirements(
        scheme="exact",
        network="eip155:8453",
        asset="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        amount="10000",
        pay_to="0x000000000000000000000000000000000000dead",
        max_timeout_seconds=60,
        extra={"name": "USD Coin", "version": "2"},
    )
    required = PaymentRequired(
        error="PAYMENT-SIGNATURE header is required",
        resource=ResourceInfo(
            url="https://multipl.dev/api/v1/jobs/mock",
            description="Fixture",
            mime_type="application/json",
        ),
        accepts=[requirements],
        extensions={"multipl": {"info": {"payment_context": "fixture-context"}}},
    )
    return encode_payment_required_header(required)


def test_request_with_x402_receipt_replay_regenerates_proof() -> None:
    header_value = _payment_required_header()
    payer = DummyPayer()
    seen_headers: list[dict[str, str] | None] = []

    def request_fn(headers: dict[str, str] | None) -> FakeResponse:
        seen_headers.append(headers)
        if headers is None:
            return FakeResponse(
                402,
                headers={PAYMENT_REQUIRED_HEADER: header_value},
                payload={
                    "payment_context": "fixture-context",
                    "recipient": "0x000000000000000000000000000000000000dead",
                    "amount": 1,
                    "asset": "usdc",
                    "network": "eip155:8453",
                },
            )

        if len(seen_headers) == 2:
            return FakeResponse(409, payload={"error": "receipt_replay"})
        return FakeResponse(201, payload={"job": {"id": "job_123", "state": "CREATED"}})

    response = request_with_x402(
        request_fn,
        payer=payer,
        allow_pay=True,
        proof_cache=ProofCache(),
    )

    assert response.status_code == 201
    assert payer.calls == 2
    assert len(seen_headers) == 3
    assert seen_headers[1] is not None
    assert seen_headers[2] is not None
    assert seen_headers[1].get("PAYMENT-SIGNATURE") != seen_headers[2].get("PAYMENT-SIGNATURE")
