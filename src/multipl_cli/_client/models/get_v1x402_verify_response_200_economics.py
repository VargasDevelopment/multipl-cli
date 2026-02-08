from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1X402VerifyResponse200Economics")


@_attrs_define
class GetV1X402VerifyResponse200Economics:
    """
    Attributes:
        platform_post_fee (str):
        result_unlock (str):
        note (str):
    """

    platform_post_fee: str
    result_unlock: str
    note: str

    def to_dict(self) -> dict[str, Any]:
        platform_post_fee = self.platform_post_fee

        result_unlock = self.result_unlock

        note = self.note

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "platform_post_fee": platform_post_fee,
                "result_unlock": result_unlock,
                "note": note,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        platform_post_fee = d.pop("platform_post_fee")

        result_unlock = d.pop("result_unlock")

        note = d.pop("note")

        get_v1x402_verify_response_200_economics = cls(
            platform_post_fee=platform_post_fee,
            result_unlock=result_unlock,
            note=note,
        )

        return get_v1x402_verify_response_200_economics
