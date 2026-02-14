from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1TrainingLeaseBody")


@_attrs_define
class PostV1TrainingLeaseBody:
    """
    Attributes:
        task_type (str | Unset):
        exercise_id (str | Unset):
    """

    task_type: str | Unset = UNSET
    exercise_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        task_type = self.task_type

        exercise_id = self.exercise_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if task_type is not UNSET:
            field_dict["taskType"] = task_type
        if exercise_id is not UNSET:
            field_dict["exerciseId"] = exercise_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_type = d.pop("taskType", UNSET)

        exercise_id = d.pop("exerciseId", UNSET)

        post_v1_training_lease_body = cls(
            task_type=task_type,
            exercise_id=exercise_id,
        )

        return post_v1_training_lease_body
