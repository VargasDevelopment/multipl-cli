from __future__ import annotations

import os
from dataclasses import dataclass

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class LocalKeyPayer(Payer):
    name: str = "local_key"

    def get_proof(self, terms: PaymentTerms) -> dict:
        private_key = os.environ.get("MULTIPL_WALLET_PRIVATE_KEY")
        if not private_key:
            raise PayerError("MULTIPL_WALLET_PRIVATE_KEY is required for local_key payer")
        raise PayerError(
            "local_key payer is not implemented: backend/docs do not define a client-side signing flow"
        )
