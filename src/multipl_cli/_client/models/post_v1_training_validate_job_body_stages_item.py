from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_training_validate_job_body_stages_item_assignment_mode import (
    PostV1TrainingValidateJobBodyStagesItemAssignmentMode,
)
from ..models.post_v1_training_validate_job_body_stages_item_visibility import (
    PostV1TrainingValidateJobBodyStagesItemVisibility,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_training_validate_job_body_stages_item_acceptance import (
        PostV1TrainingValidateJobBodyStagesItemAcceptance,
    )
    from ..models.post_v1_training_validate_job_body_stages_item_input import (
        PostV1TrainingValidateJobBodyStagesItemInput,
    )
    from ..models.post_v1_training_validate_job_body_stages_item_policy import (
        PostV1TrainingValidateJobBodyStagesItemPolicy,
    )


T = TypeVar("T", bound="PostV1TrainingValidateJobBodyStagesItem")


@_attrs_define
class PostV1TrainingValidateJobBodyStagesItem:
    """
    Attributes:
        stage_id (str):
        name (str):
        task_type (str):
        payout_cents (int):
        stage_index (int | Unset):
        input_ (PostV1TrainingValidateJobBodyStagesItemInput | Unset):
        acceptance (PostV1TrainingValidateJobBodyStagesItemAcceptance | Unset):
        deadline_seconds (int | Unset):
        visibility (PostV1TrainingValidateJobBodyStagesItemVisibility | Unset):
        assignment_mode (PostV1TrainingValidateJobBodyStagesItemAssignmentMode | Unset):
        reservation_seconds (int | Unset):
        policy (PostV1TrainingValidateJobBodyStagesItemPolicy | Unset):
    """

    stage_id: str
    name: str
    task_type: str
    payout_cents: int
    stage_index: int | Unset = UNSET
    input_: PostV1TrainingValidateJobBodyStagesItemInput | Unset = UNSET
    acceptance: PostV1TrainingValidateJobBodyStagesItemAcceptance | Unset = UNSET
    deadline_seconds: int | Unset = UNSET
    visibility: PostV1TrainingValidateJobBodyStagesItemVisibility | Unset = UNSET
    assignment_mode: PostV1TrainingValidateJobBodyStagesItemAssignmentMode | Unset = UNSET
    reservation_seconds: int | Unset = UNSET
    policy: PostV1TrainingValidateJobBodyStagesItemPolicy | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        stage_id = self.stage_id

        name = self.name

        task_type = self.task_type

        payout_cents = self.payout_cents

        stage_index = self.stage_index

        input_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_, Unset):
            input_ = self.input_.to_dict()

        acceptance: dict[str, Any] | Unset = UNSET
        if not isinstance(self.acceptance, Unset):
            acceptance = self.acceptance.to_dict()

        deadline_seconds = self.deadline_seconds

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        assignment_mode: str | Unset = UNSET
        if not isinstance(self.assignment_mode, Unset):
            assignment_mode = self.assignment_mode.value

        reservation_seconds = self.reservation_seconds

        policy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.policy, Unset):
            policy = self.policy.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stageId": stage_id,
                "name": name,
                "taskType": task_type,
                "payoutCents": payout_cents,
            }
        )
        if stage_index is not UNSET:
            field_dict["stageIndex"] = stage_index
        if input_ is not UNSET:
            field_dict["input"] = input_
        if acceptance is not UNSET:
            field_dict["acceptance"] = acceptance
        if deadline_seconds is not UNSET:
            field_dict["deadlineSeconds"] = deadline_seconds
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if assignment_mode is not UNSET:
            field_dict["assignmentMode"] = assignment_mode
        if reservation_seconds is not UNSET:
            field_dict["reservationSeconds"] = reservation_seconds
        if policy is not UNSET:
            field_dict["policy"] = policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_validate_job_body_stages_item_acceptance import (
            PostV1TrainingValidateJobBodyStagesItemAcceptance,
        )
        from ..models.post_v1_training_validate_job_body_stages_item_input import (
            PostV1TrainingValidateJobBodyStagesItemInput,
        )
        from ..models.post_v1_training_validate_job_body_stages_item_policy import (
            PostV1TrainingValidateJobBodyStagesItemPolicy,
        )

        d = dict(src_dict)
        stage_id = d.pop("stageId")

        name = d.pop("name")

        task_type = d.pop("taskType")

        payout_cents = d.pop("payoutCents")

        stage_index = d.pop("stageIndex", UNSET)

        _input_ = d.pop("input", UNSET)
        input_: PostV1TrainingValidateJobBodyStagesItemInput | Unset
        if isinstance(_input_, Unset):
            input_ = UNSET
        else:
            input_ = PostV1TrainingValidateJobBodyStagesItemInput.from_dict(_input_)

        _acceptance = d.pop("acceptance", UNSET)
        acceptance: PostV1TrainingValidateJobBodyStagesItemAcceptance | Unset
        if isinstance(_acceptance, Unset):
            acceptance = UNSET
        else:
            acceptance = PostV1TrainingValidateJobBodyStagesItemAcceptance.from_dict(_acceptance)

        deadline_seconds = d.pop("deadlineSeconds", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: PostV1TrainingValidateJobBodyStagesItemVisibility | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = PostV1TrainingValidateJobBodyStagesItemVisibility(_visibility)

        _assignment_mode = d.pop("assignmentMode", UNSET)
        assignment_mode: PostV1TrainingValidateJobBodyStagesItemAssignmentMode | Unset
        if isinstance(_assignment_mode, Unset):
            assignment_mode = UNSET
        else:
            assignment_mode = PostV1TrainingValidateJobBodyStagesItemAssignmentMode(
                _assignment_mode
            )

        reservation_seconds = d.pop("reservationSeconds", UNSET)

        _policy = d.pop("policy", UNSET)
        policy: PostV1TrainingValidateJobBodyStagesItemPolicy | Unset
        if isinstance(_policy, Unset):
            policy = UNSET
        else:
            policy = PostV1TrainingValidateJobBodyStagesItemPolicy.from_dict(_policy)

        post_v1_training_validate_job_body_stages_item = cls(
            stage_id=stage_id,
            name=name,
            task_type=task_type,
            payout_cents=payout_cents,
            stage_index=stage_index,
            input_=input_,
            acceptance=acceptance,
            deadline_seconds=deadline_seconds,
            visibility=visibility,
            assignment_mode=assignment_mode,
            reservation_seconds=reservation_seconds,
            policy=policy,
        )

        return post_v1_training_validate_job_body_stages_item
