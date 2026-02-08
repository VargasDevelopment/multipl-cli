from __future__ import annotations

from dataclasses import dataclass

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class ManualPayer(Payer):
    proof: dict | None = None

    name: str = "manual"

    def get_proof(self, terms: PaymentTerms) -> dict:
        if not self.proof:
            raise PayerError("manual proof required")
        return self.proof
