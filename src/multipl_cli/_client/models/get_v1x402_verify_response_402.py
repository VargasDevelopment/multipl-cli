from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1x402_verify_response_402_error import GetV1X402VerifyResponse402Error

T = TypeVar("T", bound="GetV1X402VerifyResponse402")


@_attrs_define
class GetV1X402VerifyResponse402:
    """
    Attributes:
        error (GetV1X402VerifyResponse402Error):
        note (str):
        skill_url (str):
        api_base (str):
    """

    error: GetV1X402VerifyResponse402Error
    note: str
    skill_url: str
    api_base: str

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        note = self.note

        skill_url = self.skill_url

        api_base = self.api_base

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
                "note": note,
                "skill_url": skill_url,
                "api_base": api_base,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = GetV1X402VerifyResponse402Error(d.pop("error"))

        note = d.pop("note")

        skill_url = d.pop("skill_url")

        api_base = d.pop("api_base")

        get_v1x402_verify_response_402 = cls(
            error=error,
            note=note,
            skill_url=skill_url,
            api_base=api_base,
        )

        return get_v1x402_verify_response_402
