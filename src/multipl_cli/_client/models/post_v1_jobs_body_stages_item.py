from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_jobs_body_stages_item_assignment_mode import (
    PostV1JobsBodyStagesItemAssignmentMode,
)
from ..models.post_v1_jobs_body_stages_item_visibility import PostV1JobsBodyStagesItemVisibility
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_jobs_body_stages_item_acceptance import PostV1JobsBodyStagesItemAcceptance
    from ..models.post_v1_jobs_body_stages_item_input import PostV1JobsBodyStagesItemInput
    from ..models.post_v1_jobs_body_stages_item_policy import PostV1JobsBodyStagesItemPolicy


T = TypeVar("T", bound="PostV1JobsBodyStagesItem")


@_attrs_define
class PostV1JobsBodyStagesItem:
    """
    Attributes:
        stage_id (str):
        name (str):
        task_type (str):
        payout_cents (int):
        stage_index (int | Unset):
        input_ (PostV1JobsBodyStagesItemInput | Unset):
        acceptance (PostV1JobsBodyStagesItemAcceptance | Unset):
        deadline_seconds (int | Unset):
        visibility (PostV1JobsBodyStagesItemVisibility | Unset):
        assignment_mode (PostV1JobsBodyStagesItemAssignmentMode | Unset):
        reservation_seconds (int | Unset):
        policy (PostV1JobsBodyStagesItemPolicy | Unset):
    """

    stage_id: str
    name: str
    task_type: str
    payout_cents: int
    stage_index: int | Unset = UNSET
    input_: PostV1JobsBodyStagesItemInput | Unset = UNSET
    acceptance: PostV1JobsBodyStagesItemAcceptance | Unset = UNSET
    deadline_seconds: int | Unset = UNSET
    visibility: PostV1JobsBodyStagesItemVisibility | Unset = UNSET
    assignment_mode: PostV1JobsBodyStagesItemAssignmentMode | Unset = UNSET
    reservation_seconds: int | Unset = UNSET
    policy: PostV1JobsBodyStagesItemPolicy | Unset = UNSET

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
        from ..models.post_v1_jobs_body_stages_item_acceptance import (
            PostV1JobsBodyStagesItemAcceptance,
        )
        from ..models.post_v1_jobs_body_stages_item_input import PostV1JobsBodyStagesItemInput
        from ..models.post_v1_jobs_body_stages_item_policy import PostV1JobsBodyStagesItemPolicy

        d = dict(src_dict)
        stage_id = d.pop("stageId")

        name = d.pop("name")

        task_type = d.pop("taskType")

        payout_cents = d.pop("payoutCents")

        stage_index = d.pop("stageIndex", UNSET)

        _input_ = d.pop("input", UNSET)
        input_: PostV1JobsBodyStagesItemInput | Unset
        if isinstance(_input_, Unset):
            input_ = UNSET
        else:
            input_ = PostV1JobsBodyStagesItemInput.from_dict(_input_)

        _acceptance = d.pop("acceptance", UNSET)
        acceptance: PostV1JobsBodyStagesItemAcceptance | Unset
        if isinstance(_acceptance, Unset):
            acceptance = UNSET
        else:
            acceptance = PostV1JobsBodyStagesItemAcceptance.from_dict(_acceptance)

        deadline_seconds = d.pop("deadlineSeconds", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: PostV1JobsBodyStagesItemVisibility | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = PostV1JobsBodyStagesItemVisibility(_visibility)

        _assignment_mode = d.pop("assignmentMode", UNSET)
        assignment_mode: PostV1JobsBodyStagesItemAssignmentMode | Unset
        if isinstance(_assignment_mode, Unset):
            assignment_mode = UNSET
        else:
            assignment_mode = PostV1JobsBodyStagesItemAssignmentMode(_assignment_mode)

        reservation_seconds = d.pop("reservationSeconds", UNSET)

        _policy = d.pop("policy", UNSET)
        policy: PostV1JobsBodyStagesItemPolicy | Unset
        if isinstance(_policy, Unset):
            policy = UNSET
        else:
            policy = PostV1JobsBodyStagesItemPolicy.from_dict(_policy)

        post_v1_jobs_body_stages_item = cls(
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

        return post_v1_jobs_body_stages_item
