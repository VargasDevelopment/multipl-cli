from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1X402VerifyResponse200Links")


@_attrs_define
class GetV1X402VerifyResponse200Links:
    """
    Attributes:
        skill_url (str):
        docs_url (str):
        homepage (str):
    """

    skill_url: str
    docs_url: str
    homepage: str

    def to_dict(self) -> dict[str, Any]:
        skill_url = self.skill_url

        docs_url = self.docs_url

        homepage = self.homepage

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "skill_url": skill_url,
                "docs_url": docs_url,
                "homepage": homepage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        skill_url = d.pop("skill_url")

        docs_url = d.pop("docs_url")

        homepage = d.pop("homepage")

        get_v1x402_verify_response_200_links = cls(
            skill_url=skill_url,
            docs_url=docs_url,
            homepage=homepage,
        )

        return get_v1x402_verify_response_200_links
