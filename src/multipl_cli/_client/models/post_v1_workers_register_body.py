from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_workers_register_body_metadata import PostV1WorkersRegisterBodyMetadata


T = TypeVar("T", bound="PostV1WorkersRegisterBody")


@_attrs_define
class PostV1WorkersRegisterBody:
    """
    Attributes:
        name (str):
        description (str | Unset):
        metadata (PostV1WorkersRegisterBodyMetadata | Unset):
    """

    name: str
    description: str | Unset = UNSET
    metadata: PostV1WorkersRegisterBodyMetadata | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_workers_register_body_metadata import (
            PostV1WorkersRegisterBodyMetadata,
        )

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: PostV1WorkersRegisterBodyMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostV1WorkersRegisterBodyMetadata.from_dict(_metadata)

        post_v1_workers_register_body = cls(
            name=name,
            description=description,
            metadata=metadata,
        )

        return post_v1_workers_register_body
