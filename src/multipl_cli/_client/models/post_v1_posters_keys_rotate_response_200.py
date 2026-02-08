from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersKeysRotateResponse200")


@_attrs_define
class PostV1PostersKeysRotateResponse200:
    """
    Attributes:
        api_key (str):
    """

    api_key: str

    def to_dict(self) -> dict[str, Any]:
        api_key = self.api_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "api_key": api_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_key = d.pop("api_key")

        post_v1_posters_keys_rotate_response_200 = cls(
            api_key=api_key,
        )

        return post_v1_posters_keys_rotate_response_200
