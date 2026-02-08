from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_jobs_job_id_review_body_decision import PostV1JobsJobIdReviewBodyDecision
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1JobsJobIdReviewBody")


@_attrs_define
class PostV1JobsJobIdReviewBody:
    """
    Attributes:
        decision (PostV1JobsJobIdReviewBodyDecision):
        reason (str | Unset):
    """

    decision: PostV1JobsJobIdReviewBodyDecision
    reason: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        decision = self.decision.value

        reason = self.reason

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "decision": decision,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision = PostV1JobsJobIdReviewBodyDecision(d.pop("decision"))

        reason = d.pop("reason", UNSET)

        post_v1_jobs_job_id_review_body = cls(
            decision=decision,
            reason=reason,
        )

        return post_v1_jobs_job_id_review_body
