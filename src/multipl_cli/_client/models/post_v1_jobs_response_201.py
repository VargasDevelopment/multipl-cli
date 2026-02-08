from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_jobs_response_201_job import PostV1JobsResponse201Job


T = TypeVar("T", bound="PostV1JobsResponse201")


@_attrs_define
class PostV1JobsResponse201:
    """
    Attributes:
        job (PostV1JobsResponse201Job):
    """

    job: PostV1JobsResponse201Job

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
        from ..models.post_v1_jobs_response_201_job import PostV1JobsResponse201Job

        d = dict(src_dict)
        job = PostV1JobsResponse201Job.from_dict(d.pop("job"))

        post_v1_jobs_response_201 = cls(
            job=job,
        )

        return post_v1_jobs_response_201
