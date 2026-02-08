from __future__ import annotations

from abc import ABC, abstractmethod

from multipl_cli.x402.terms import PaymentTerms


class PayerError(RuntimeError):
    pass


class Payer(ABC):
    name: str

    @abstractmethod
    def get_proof(self, terms: PaymentTerms) -> dict:
        raise NotImplementedError
