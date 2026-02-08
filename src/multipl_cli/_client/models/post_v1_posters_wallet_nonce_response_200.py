from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersWalletNonceResponse200")


@_attrs_define
class PostV1PostersWalletNonceResponse200:
    """
    Attributes:
        address (str):
        nonce (str):
        message (str):
        expires_at (str):
    """

    address: str
    nonce: str
    message: str
    expires_at: str

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        nonce = self.nonce

        message = self.message

        expires_at = self.expires_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "address": address,
                "nonce": nonce,
                "message": message,
                "expiresAt": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address")

        nonce = d.pop("nonce")

        message = d.pop("message")

        expires_at = d.pop("expiresAt")

        post_v1_posters_wallet_nonce_response_200 = cls(
            address=address,
            nonce=nonce,
            message=message,
            expires_at=expires_at,
        )

        return post_v1_posters_wallet_nonce_response_200
