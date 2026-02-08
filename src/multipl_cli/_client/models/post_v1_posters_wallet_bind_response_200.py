from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersWalletBindResponse200")


@_attrs_define
class PostV1PostersWalletBindResponse200:
    """
    Attributes:
        wallet_address (str):
        wallet_bound_at (str):
    """

    wallet_address: str
    wallet_bound_at: str

    def to_dict(self) -> dict[str, Any]:
        wallet_address = self.wallet_address

        wallet_bound_at = self.wallet_bound_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "walletAddress": wallet_address,
                "walletBoundAt": wallet_bound_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        wallet_address = d.pop("walletAddress")

        wallet_bound_at = d.pop("walletBoundAt")

        post_v1_posters_wallet_bind_response_200 = cls(
            wallet_address=wallet_address,
            wallet_bound_at=wallet_bound_at,
        )

        return post_v1_posters_wallet_bind_response_200
