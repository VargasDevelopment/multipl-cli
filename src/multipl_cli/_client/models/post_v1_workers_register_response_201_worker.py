from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1WorkersRegisterResponse201Worker")


@_attrs_define
class PostV1WorkersRegisterResponse201Worker:
    """
    Attributes:
        id (str):
        name (str):
        description (None | str):
        is_claimed (bool):
    """

    id: str
    name: str
    description: None | str
    is_claimed: bool

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description: None | str
        description = self.description

        is_claimed = self.is_claimed

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "isClaimed": is_claimed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        is_claimed = d.pop("isClaimed")

        post_v1_workers_register_response_201_worker = cls(
            id=id,
            name=name,
            description=description,
            is_claimed=is_claimed,
        )

        return post_v1_workers_register_response_201_worker
