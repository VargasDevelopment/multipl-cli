from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_training_lease_response_200_mode import PostV1TrainingLeaseResponse200Mode

if TYPE_CHECKING:
    from ..models.post_v1_training_lease_response_200_exercise import (
        PostV1TrainingLeaseResponse200Exercise,
    )
    from ..models.post_v1_training_lease_response_200_lease import (
        PostV1TrainingLeaseResponse200Lease,
    )


T = TypeVar("T", bound="PostV1TrainingLeaseResponse200")


@_attrs_define
class PostV1TrainingLeaseResponse200:
    """
    Attributes:
        mode (PostV1TrainingLeaseResponse200Mode):
        lease (PostV1TrainingLeaseResponse200Lease):
        exercise (PostV1TrainingLeaseResponse200Exercise):
    """

    mode: PostV1TrainingLeaseResponse200Mode
    lease: PostV1TrainingLeaseResponse200Lease
    exercise: PostV1TrainingLeaseResponse200Exercise

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        lease = self.lease.to_dict()

        exercise = self.exercise.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
                "lease": lease,
                "exercise": exercise,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_lease_response_200_exercise import (
            PostV1TrainingLeaseResponse200Exercise,
        )
        from ..models.post_v1_training_lease_response_200_lease import (
            PostV1TrainingLeaseResponse200Lease,
        )

        d = dict(src_dict)
        mode = PostV1TrainingLeaseResponse200Mode(d.pop("mode"))

        lease = PostV1TrainingLeaseResponse200Lease.from_dict(d.pop("lease"))

        exercise = PostV1TrainingLeaseResponse200Exercise.from_dict(d.pop("exercise"))

        post_v1_training_lease_response_200 = cls(
            mode=mode,
            lease=lease,
            exercise=exercise,
        )

        return post_v1_training_lease_response_200
