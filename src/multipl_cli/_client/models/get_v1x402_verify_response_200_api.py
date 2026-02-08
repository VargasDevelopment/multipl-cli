from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1X402VerifyResponse200Api")


@_attrs_define
class GetV1X402VerifyResponse200Api:
    """
    Attributes:
        api_base (str):
        api_version (str):
        api_base_v1 (str):
        verify_url (str):
    """

    api_base: str
    api_version: str
    api_base_v1: str
    verify_url: str

    def to_dict(self) -> dict[str, Any]:
        api_base = self.api_base

        api_version = self.api_version

        api_base_v1 = self.api_base_v1

        verify_url = self.verify_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "api_base": api_base,
                "api_version": api_version,
                "api_base_v1": api_base_v1,
                "verify_url": verify_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_base = d.pop("api_base")

        api_version = d.pop("api_version")

        api_base_v1 = d.pop("api_base_v1")

        verify_url = d.pop("verify_url")

        get_v1x402_verify_response_200_api = cls(
            api_base=api_base,
            api_version=api_version,
            api_base_v1=api_base_v1,
            verify_url=verify_url,
        )

        return get_v1x402_verify_response_200_api
