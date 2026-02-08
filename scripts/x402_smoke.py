from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

from x402.http import decode_payment_required_header
from x402.schemas import PaymentRequired, PaymentRequirements

from multipl_cli.x402.payer_local_key import LocalKeyPayer
from multipl_cli.x402.proof import proof_to_header_value
from multipl_cli.x402.terms import PaymentTerms


def _select_requirement(payment_required: PaymentRequired) -> PaymentRequirements:
    for requirement in payment_required.accepts:
        if requirement.scheme == "exact":
            return requirement
    return payment_required.accepts[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="x402 LocalKeyPayer smoke test")
    parser.add_argument(
        "--header-file",
        default="fixtures/payment_required.txt",
        help="Path to PAYMENT-REQUIRED header fixture",
    )
    parser.add_argument(
        "--private-key",
        default=None,
        help="Private key override (hex, with or without 0x)",
    )
    args = parser.parse_args()

    if args.private_key:
        os.environ["MULTIPL_WALLET_PRIVATE_KEY"] = args.private_key

    header_path = Path(args.header_file)
    header_value = header_path.read_text().strip()
    payment_required = decode_payment_required_header(header_value)
    if not isinstance(payment_required, PaymentRequired):
        raise SystemExit("Unsupported x402 version in header fixture")

    requirement = _select_requirement(payment_required)
    extensions = payment_required.extensions or {}
    payment_context = (
        extensions.get("multipl", {}).get("info", {}).get("payment_context")
        if isinstance(extensions, dict)
        else None
    )

    terms = PaymentTerms(
        payment_required=payment_required,
        requirement=requirement,
        recipient=requirement.pay_to,
        amount=requirement.amount,
        asset=str(requirement.asset),
        network=str(requirement.network),
        payment_context=payment_context,
    )

    payer = LocalKeyPayer()
    proof = payer.get_proof(terms)
    print("proof_keys=", sorted(proof.keys()))
    print("accepted=", proof.get("accepted"))

    header_value = proof_to_header_value(proof)
    decoded = base64.b64decode(header_value).decode("utf-8")
    round_trip = json.loads(decoded)
    assert isinstance(round_trip, dict)
    assert "paymentPayload" in round_trip and "paymentRequirements" in round_trip
    print("round_trip_ok=True")


if __name__ == "__main__":
    main()
