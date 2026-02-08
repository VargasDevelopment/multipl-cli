from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PutV1WorkersMeWalletResponse200Wallet")


@_attrs_define
class PutV1WorkersMeWalletResponse200Wallet:
    """
    Attributes:
        worker_id (str):
        wallet_address (str):
        network (str):
        asset (str):
        updated_at (str):
    """

    worker_id: str
    wallet_address: str
    network: str
    asset: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        worker_id = self.worker_id

        wallet_address = self.wallet_address

        network = self.network

        asset = self.asset

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "workerId": worker_id,
                "walletAddress": wallet_address,
                "network": network,
                "asset": asset,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        worker_id = d.pop("workerId")

        wallet_address = d.pop("walletAddress")

        network = d.pop("network")

        asset = d.pop("asset")

        updated_at = d.pop("updatedAt")

        put_v1_workers_me_wallet_response_200_wallet = cls(
            worker_id=worker_id,
            wallet_address=wallet_address,
            network=network,
            asset=asset,
            updated_at=updated_at,
        )

        return put_v1_workers_me_wallet_response_200_wallet
