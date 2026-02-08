from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_jobs_body_acceptance import PostV1JobsBodyAcceptance
    from ..models.post_v1_jobs_body_input import PostV1JobsBodyInput


T = TypeVar("T", bound="PostV1JobsBody")


@_attrs_define
class PostV1JobsBody:
    """
    Attributes:
        task_type (str):
        input_ (PostV1JobsBodyInput):
        acceptance (PostV1JobsBodyAcceptance | Unset):
        requested_model (str | Unset):
        estimated_tokens (int | Unset):
        deadline_seconds (int | Unset):
        payout_cents (int | Unset):
        job_ttl_seconds (int | Unset):
    """

    task_type: str
    input_: PostV1JobsBodyInput
    acceptance: PostV1JobsBodyAcceptance | Unset = UNSET
    requested_model: str | Unset = UNSET
    estimated_tokens: int | Unset = UNSET
    deadline_seconds: int | Unset = UNSET
    payout_cents: int | Unset = UNSET
    job_ttl_seconds: int | Unset = UNSET

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_jobs_body_acceptance import PostV1JobsBodyAcceptance
        from ..models.post_v1_jobs_body_input import PostV1JobsBodyInput

        d = dict(src_dict)
        task_type = d.pop("taskType")

        input_ = PostV1JobsBodyInput.from_dict(d.pop("input"))

        _acceptance = d.pop("acceptance", UNSET)
        acceptance: PostV1JobsBodyAcceptance | Unset
        if isinstance(_acceptance, Unset):
            acceptance = UNSET
        else:
            acceptance = PostV1JobsBodyAcceptance.from_dict(_acceptance)

        requested_model = d.pop("requestedModel", UNSET)

        estimated_tokens = d.pop("estimatedTokens", UNSET)

        deadline_seconds = d.pop("deadlineSeconds", UNSET)

        payout_cents = d.pop("payoutCents", UNSET)

        job_ttl_seconds = d.pop("jobTtlSeconds", UNSET)

        post_v1_jobs_body = cls(
            task_type=task_type,
            input_=input_,
            acceptance=acceptance,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            payout_cents=payout_cents,
            job_ttl_seconds=job_ttl_seconds,
        )

        return post_v1_jobs_body
