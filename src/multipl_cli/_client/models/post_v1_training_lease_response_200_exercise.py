from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract import (
        PostV1TrainingLeaseResponse200ExerciseAcceptanceContract,
    )
    from ..models.post_v1_training_lease_response_200_exercise_input import (
        PostV1TrainingLeaseResponse200ExerciseInput,
    )


T = TypeVar("T", bound="PostV1TrainingLeaseResponse200Exercise")


@_attrs_define
class PostV1TrainingLeaseResponse200Exercise:
    """
    Attributes:
        id (str):
        title (str):
        task_type (str):
        prompt (str):
        input_ (PostV1TrainingLeaseResponse200ExerciseInput):
        acceptance_contract (PostV1TrainingLeaseResponse200ExerciseAcceptanceContract):
    """

    id: str
    title: str
    task_type: str
    prompt: str
    input_: PostV1TrainingLeaseResponse200ExerciseInput
    acceptance_contract: PostV1TrainingLeaseResponse200ExerciseAcceptanceContract

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        task_type = self.task_type

        prompt = self.prompt

        input_ = self.input_.to_dict()

        acceptance_contract = self.acceptance_contract.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "title": title,
                "taskType": task_type,
                "prompt": prompt,
                "input": input_,
                "acceptanceContract": acceptance_contract,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract import (
            PostV1TrainingLeaseResponse200ExerciseAcceptanceContract,
        )
        from ..models.post_v1_training_lease_response_200_exercise_input import (
            PostV1TrainingLeaseResponse200ExerciseInput,
        )

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        task_type = d.pop("taskType")

        prompt = d.pop("prompt")

        input_ = PostV1TrainingLeaseResponse200ExerciseInput.from_dict(d.pop("input"))

        acceptance_contract = PostV1TrainingLeaseResponse200ExerciseAcceptanceContract.from_dict(
            d.pop("acceptanceContract")
        )

        post_v1_training_lease_response_200_exercise = cls(
            id=id,
            title=title,
            task_type=task_type,
            prompt=prompt,
            input_=input_,
            acceptance_contract=acceptance_contract,
        )

        return post_v1_training_lease_response_200_exercise
