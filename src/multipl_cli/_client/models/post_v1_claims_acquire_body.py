from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1ClaimsAcquireBody")


@_attrs_define
class PostV1ClaimsAcquireBody:
    """
    Attributes:
        task_type (str | Unset):
        job_id (str | Unset):
    """

    task_type: str | Unset = UNSET
    job_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        task_type = self.task_type

        job_id = self.job_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if task_type is not UNSET:
            field_dict["taskType"] = task_type
        if job_id is not UNSET:
            field_dict["jobId"] = job_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_type = d.pop("taskType", UNSET)

        job_id = d.pop("jobId", UNSET)

        post_v1_claims_acquire_body = cls(
            task_type=task_type,
            job_id=job_id,
        )

        return post_v1_claims_acquire_body
