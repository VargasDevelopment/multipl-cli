from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_response_200_job import GetV1JobsJobIdResponse200Job


T = TypeVar("T", bound="GetV1JobsJobIdResponse200")


@_attrs_define
class GetV1JobsJobIdResponse200:
    """
    Attributes:
        job (GetV1JobsJobIdResponse200Job):
    """

    job: GetV1JobsJobIdResponse200Job

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
        from ..models.get_v1_jobs_job_id_response_200_job import GetV1JobsJobIdResponse200Job

        d = dict(src_dict)
        job = GetV1JobsJobIdResponse200Job.from_dict(d.pop("job"))

        get_v1_jobs_job_id_response_200 = cls(
            job=job,
        )

        return get_v1_jobs_job_id_response_200
