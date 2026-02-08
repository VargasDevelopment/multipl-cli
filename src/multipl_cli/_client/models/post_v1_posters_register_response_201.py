from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1PostersRegisterResponse201")


@_attrs_define
class PostV1PostersRegisterResponse201:
    """
    Attributes:
        poster_id (str):
        api_key (str):
    """

    poster_id: str
    api_key: str

    def to_dict(self) -> dict[str, Any]:
        poster_id = self.poster_id

        api_key = self.api_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "poster_id": poster_id,
                "api_key": api_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        poster_id = d.pop("poster_id")

        api_key = d.pop("api_key")

        post_v1_posters_register_response_201 = cls(
            poster_id=poster_id,
            api_key=api_key,
        )

        return post_v1_posters_register_response_201
