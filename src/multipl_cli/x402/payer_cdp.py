from __future__ import annotations

from dataclasses import dataclass

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class CdpPayer(Payer):
    name: str = "cdp"

    def get_proof(self, terms: PaymentTerms) -> dict:
        raise PayerError(
            "cdp payer is not implemented: CDP wallet signing isn't wired in the CLI yet. "
            "Use --payer local_key (with MULTIPL_WALLET_PRIVATE_KEY) or manual proof."
        )
