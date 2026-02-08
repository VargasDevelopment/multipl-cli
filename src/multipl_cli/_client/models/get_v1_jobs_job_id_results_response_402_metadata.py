from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1JobsJobIdResultsResponse402Metadata")


@_attrs_define
class GetV1JobsJobIdResultsResponse402Metadata:
    """
    Attributes:
        job_id (str):
        task_type (str):
        submitted_at (str):
    """

    job_id: str
    task_type: str
    submitted_at: str

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        task_type = self.task_type

        submitted_at = self.submitted_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobId": job_id,
                "taskType": task_type,
                "submittedAt": submitted_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("jobId")

        task_type = d.pop("taskType")

        submitted_at = d.pop("submittedAt")

        get_v1_jobs_job_id_results_response_402_metadata = cls(
            job_id=job_id,
            task_type=task_type,
            submitted_at=submitted_at,
        )

        return get_v1_jobs_job_id_results_response_402_metadata
