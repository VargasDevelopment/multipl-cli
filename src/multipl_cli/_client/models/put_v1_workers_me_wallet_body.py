from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutV1WorkersMeWalletBody")


@_attrs_define
class PutV1WorkersMeWalletBody:
    """
    Attributes:
        address (str):
        network (str | Unset):
        asset (str | Unset):
    """

    address: str
    network: str | Unset = UNSET
    asset: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        network = self.network

        asset = self.asset

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "address": address,
            }
        )
        if network is not UNSET:
            field_dict["network"] = network
        if asset is not UNSET:
            field_dict["asset"] = asset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address")

        network = d.pop("network", UNSET)

        asset = d.pop("asset", UNSET)

        put_v1_workers_me_wallet_body = cls(
            address=address,
            network=network,
            asset=asset,
        )

        return put_v1_workers_me_wallet_body
