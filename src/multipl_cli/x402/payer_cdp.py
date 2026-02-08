from __future__ import annotations

from dataclasses import dataclass

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class CdpPayer(Payer):
    name: str = "cdp"

    def get_proof(self, terms: PaymentTerms) -> dict:
        raise PayerError(
            "cdp payer is not implemented: backend/docs do not define a client-side integration"
        )
