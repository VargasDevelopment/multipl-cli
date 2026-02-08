from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.put_v1_workers_me_wallet_response_200_wallet import (
        PutV1WorkersMeWalletResponse200Wallet,
    )


T = TypeVar("T", bound="PutV1WorkersMeWalletResponse200")


@_attrs_define
class PutV1WorkersMeWalletResponse200:
    """
    Attributes:
        wallet (PutV1WorkersMeWalletResponse200Wallet):
    """

    wallet: PutV1WorkersMeWalletResponse200Wallet

    def to_dict(self) -> dict[str, Any]:
        wallet = self.wallet.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "wallet": wallet,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_v1_workers_me_wallet_response_200_wallet import (
            PutV1WorkersMeWalletResponse200Wallet,
        )

        d = dict(src_dict)
        wallet = PutV1WorkersMeWalletResponse200Wallet.from_dict(d.pop("wallet"))

        put_v1_workers_me_wallet_response_200 = cls(
            wallet=wallet,
        )

        return put_v1_workers_me_wallet_response_200
