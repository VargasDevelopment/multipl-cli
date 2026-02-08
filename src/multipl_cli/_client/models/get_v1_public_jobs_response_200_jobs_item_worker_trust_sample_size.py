from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize")


@_attrs_define
class GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize:
    """
    Attributes:
        submissions_all_time (int):
    """

    submissions_all_time: int

    def to_dict(self) -> dict[str, Any]:
        submissions_all_time = self.submissions_all_time

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "submissionsAllTime": submissions_all_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        submissions_all_time = d.pop("submissionsAllTime")

        get_v1_public_jobs_response_200_jobs_item_worker_trust_sample_size = cls(
            submissions_all_time=submissions_all_time,
        )

        return get_v1_public_jobs_response_200_jobs_item_worker_trust_sample_size
