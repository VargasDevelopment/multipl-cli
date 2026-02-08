from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersWalletNonceBody")


@_attrs_define
class PostV1PostersWalletNonceBody:
    """
    Attributes:
        address (str):
    """

    address: str

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "address": address,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address")

        post_v1_posters_wallet_nonce_body = cls(
            address=address,
        )

        return post_v1_posters_wallet_nonce_body
