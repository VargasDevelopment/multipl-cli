from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1WorkersClaimBody")


@_attrs_define
class PostV1WorkersClaimBody:
    """
    Attributes:
        claim_token (str):
        verification_code (str | Unset):
    """

    claim_token: str
    verification_code: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        claim_token = self.claim_token

        verification_code = self.verification_code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "claim_token": claim_token,
            }
        )
        if verification_code is not UNSET:
            field_dict["verification_code"] = verification_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        claim_token = d.pop("claim_token")

        verification_code = d.pop("verification_code", UNSET)

        post_v1_workers_claim_body = cls(
            claim_token=claim_token,
            verification_code=verification_code,
        )

        return post_v1_workers_claim_body
