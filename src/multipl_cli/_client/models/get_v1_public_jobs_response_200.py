from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_response_200_jobs_item import (
        GetV1PublicJobsResponse200JobsItem,
    )


T = TypeVar("T", bound="GetV1PublicJobsResponse200")


@_attrs_define
class GetV1PublicJobsResponse200:
    """
    Attributes:
        jobs (list[GetV1PublicJobsResponse200JobsItem]):
        next_cursor (None | str):
    """

    jobs: list[GetV1PublicJobsResponse200JobsItem]
    next_cursor: None | str

    def to_dict(self) -> dict[str, Any]:
        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobs": jobs,
                "nextCursor": next_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_response_200_jobs_item import (
            GetV1PublicJobsResponse200JobsItem,
        )

        d = dict(src_dict)
        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = GetV1PublicJobsResponse200JobsItem.from_dict(jobs_item_data)

            jobs.append(jobs_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("nextCursor"))

        get_v1_public_jobs_response_200 = cls(
            jobs=jobs,
            next_cursor=next_cursor,
        )

        return get_v1_public_jobs_response_200
