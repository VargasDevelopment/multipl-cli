from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_training_validate_job_body_acceptance import (
        PostV1TrainingValidateJobBodyAcceptance,
    )
    from ..models.post_v1_training_validate_job_body_input import PostV1TrainingValidateJobBodyInput
    from ..models.post_v1_training_validate_job_body_stages_item import (
        PostV1TrainingValidateJobBodyStagesItem,
    )


T = TypeVar("T", bound="PostV1TrainingValidateJobBody")


@_attrs_define
class PostV1TrainingValidateJobBody:
    """
    Attributes:
        task_type (str):
        input_ (PostV1TrainingValidateJobBodyInput):
        acceptance (PostV1TrainingValidateJobBodyAcceptance | Unset):
        requested_model (str | Unset):
        estimated_tokens (int | Unset):
        deadline_seconds (int | Unset):
        payout_cents (int | Unset):
        job_ttl_seconds (int | Unset):
        stages (list[PostV1TrainingValidateJobBodyStagesItem] | Unset):
    """

    task_type: str
    input_: PostV1TrainingValidateJobBodyInput
    acceptance: PostV1TrainingValidateJobBodyAcceptance | Unset = UNSET
    requested_model: str | Unset = UNSET
    estimated_tokens: int | Unset = UNSET
    deadline_seconds: int | Unset = UNSET
    payout_cents: int | Unset = UNSET
    job_ttl_seconds: int | Unset = UNSET
    stages: list[PostV1TrainingValidateJobBodyStagesItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        task_type = self.task_type

        input_ = self.input_.to_dict()

        acceptance: dict[str, Any] | Unset = UNSET
        if not isinstance(self.acceptance, Unset):
            acceptance = self.acceptance.to_dict()

        requested_model = self.requested_model

        estimated_tokens = self.estimated_tokens

        deadline_seconds = self.deadline_seconds

        payout_cents = self.payout_cents

        job_ttl_seconds = self.job_ttl_seconds

        stages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.stages, Unset):
            stages = []
            for stages_item_data in self.stages:
                stages_item = stages_item_data.to_dict()
                stages.append(stages_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "taskType": task_type,
                "input": input_,
            }
        )
        if acceptance is not UNSET:
            field_dict["acceptance"] = acceptance
        if requested_model is not UNSET:
            field_dict["requestedModel"] = requested_model
        if estimated_tokens is not UNSET:
            field_dict["estimatedTokens"] = estimated_tokens
        if deadline_seconds is not UNSET:
            field_dict["deadlineSeconds"] = deadline_seconds
        if payout_cents is not UNSET:
            field_dict["payoutCents"] = payout_cents
        if job_ttl_seconds is not UNSET:
            field_dict["jobTtlSeconds"] = job_ttl_seconds
        if stages is not UNSET:
            field_dict["stages"] = stages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_validate_job_body_acceptance import (
            PostV1TrainingValidateJobBodyAcceptance,
        )
        from ..models.post_v1_training_validate_job_body_input import (
            PostV1TrainingValidateJobBodyInput,
        )
        from ..models.post_v1_training_validate_job_body_stages_item import (
            PostV1TrainingValidateJobBodyStagesItem,
        )

        d = dict(src_dict)
        task_type = d.pop("taskType")

        input_ = PostV1TrainingValidateJobBodyInput.from_dict(d.pop("input"))

        _acceptance = d.pop("acceptance", UNSET)
        acceptance: PostV1TrainingValidateJobBodyAcceptance | Unset
        if isinstance(_acceptance, Unset):
            acceptance = UNSET
        else:
            acceptance = PostV1TrainingValidateJobBodyAcceptance.from_dict(_acceptance)

        requested_model = d.pop("requestedModel", UNSET)

        estimated_tokens = d.pop("estimatedTokens", UNSET)

        deadline_seconds = d.pop("deadlineSeconds", UNSET)

        payout_cents = d.pop("payoutCents", UNSET)

        job_ttl_seconds = d.pop("jobTtlSeconds", UNSET)

        _stages = d.pop("stages", UNSET)
        stages: list[PostV1TrainingValidateJobBodyStagesItem] | Unset = UNSET
        if _stages is not UNSET:
            stages = []
            for stages_item_data in _stages:
                stages_item = PostV1TrainingValidateJobBodyStagesItem.from_dict(stages_item_data)

                stages.append(stages_item)

        post_v1_training_validate_job_body = cls(
            task_type=task_type,
            input_=input_,
            acceptance=acceptance,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            payout_cents=payout_cents,
            job_ttl_seconds=job_ttl_seconds,
            stages=stages,
        )

        return post_v1_training_validate_job_body
