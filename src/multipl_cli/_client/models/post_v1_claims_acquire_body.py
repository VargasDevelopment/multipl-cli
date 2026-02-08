from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1ClaimsAcquireBody")


@_attrs_define
class PostV1ClaimsAcquireBody:
    """
    Attributes:
        task_type (str):
    """

    task_type: str

    def to_dict(self) -> dict[str, Any]:
        task_type = self.task_type

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "taskType": task_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_type = d.pop("taskType")

        post_v1_claims_acquire_body = cls(
            task_type=task_type,
        )

        return post_v1_claims_acquire_body
