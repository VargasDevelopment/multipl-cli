from __future__ import annotations

import os
from dataclasses import dataclass

from eth_account import Account
from x402 import x402ClientSync
from x402.mechanisms.evm.exact import register_exact_evm_client
from x402.mechanisms.evm.signers import EthAccountSigner

from multipl_cli.x402.payer_base import Payer, PayerError
from multipl_cli.x402.terms import PaymentTerms


@dataclass
class LocalKeyPayer(Payer):
    name: str = "local_key"

    def get_proof(self, terms: PaymentTerms) -> dict:
        private_key = os.environ.get("MULTIPL_WALLET_PRIVATE_KEY")
        if not private_key:
            raise PayerError("MULTIPL_WALLET_PRIVATE_KEY is required for local_key payer")
        key = private_key.strip()
        if not key:
            raise PayerError("MULTIPL_WALLET_PRIVATE_KEY is required for local_key payer")
        if not key.startswith("0x"):
            key = f"0x{key}"

        account = Account.from_key(key)
        signer = EthAccountSigner(account)

        client = x402ClientSync()
        register_exact_evm_client(client, signer)

        try:
            payload = client.create_payment_payload(
                terms.payment_required,
                resource=terms.payment_required.resource,
                extensions=terms.payment_required.extensions,
            )
        except Exception as exc:
            raise PayerError(f"failed to build x402 payment payload: {exc}") from exc

        payload_dict = payload.model_dump(by_alias=True, exclude_none=True)
        requirements_dict = terms.requirement.model_dump(by_alias=True, exclude_none=True)
        return {
            "x402Version": terms.payment_required.x402_version,
            "paymentPayload": payload_dict,
            "paymentRequirements": requirements_dict,
        }
