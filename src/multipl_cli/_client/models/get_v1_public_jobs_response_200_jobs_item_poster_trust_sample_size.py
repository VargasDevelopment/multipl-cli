from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize")


@_attrs_define
class GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize:
    """
    Attributes:
        jobs_posted_all_time (int):
    """

    jobs_posted_all_time: int

    def to_dict(self) -> dict[str, Any]:
        jobs_posted_all_time = self.jobs_posted_all_time

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobsPostedAllTime": jobs_posted_all_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        jobs_posted_all_time = d.pop("jobsPostedAllTime")

        get_v1_public_jobs_response_200_jobs_item_poster_trust_sample_size = cls(
            jobs_posted_all_time=jobs_posted_all_time,
        )

        return get_v1_public_jobs_response_200_jobs_item_poster_trust_sample_size
