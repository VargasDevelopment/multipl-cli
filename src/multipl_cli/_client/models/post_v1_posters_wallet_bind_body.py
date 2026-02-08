from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersWalletBindBody")


@_attrs_define
class PostV1PostersWalletBindBody:
    """
    Attributes:
        address (str):
        nonce (str):
        signature (str):
    """

    address: str
    nonce: str
    signature: str

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        nonce = self.nonce

        signature = self.signature

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "address": address,
                "nonce": nonce,
                "signature": signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address")

        nonce = d.pop("nonce")

        signature = d.pop("signature")

        post_v1_posters_wallet_bind_body = cls(
            address=address,
            nonce=nonce,
            signature=signature,
        )

        return post_v1_posters_wallet_bind_body
