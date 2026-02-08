from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_jobs_job_id_review_response_200_job import (
        PostV1JobsJobIdReviewResponse200Job,
    )


T = TypeVar("T", bound="PostV1JobsJobIdReviewResponse200")


@_attrs_define
class PostV1JobsJobIdReviewResponse200:
    """
    Attributes:
        job (PostV1JobsJobIdReviewResponse200Job):
    """

    job: PostV1JobsJobIdReviewResponse200Job

    def to_dict(self) -> dict[str, Any]:
        job = self.job.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "job": job,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_jobs_job_id_review_response_200_job import (
            PostV1JobsJobIdReviewResponse200Job,
        )

        d = dict(src_dict)
        job = PostV1JobsJobIdReviewResponse200Job.from_dict(d.pop("job"))

        post_v1_jobs_job_id_review_response_200 = cls(
            job=job,
        )

        return post_v1_jobs_job_id_review_response_200
