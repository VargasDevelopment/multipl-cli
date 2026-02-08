from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1JobsJobIdPreviewResponse200Type1Metadata")


@_attrs_define
class GetV1JobsJobIdPreviewResponse200Type1Metadata:
    """
    Attributes:
        job_id (str):
        task_type (str):
        submitted_at (str):
        worker_provided (bool):
        preview_byte_size (int):
    """

    job_id: str
    task_type: str
    submitted_at: str
    worker_provided: bool
    preview_byte_size: int

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        task_type = self.task_type

        submitted_at = self.submitted_at

        worker_provided = self.worker_provided

        preview_byte_size = self.preview_byte_size

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobId": job_id,
                "taskType": task_type,
                "submittedAt": submitted_at,
                "workerProvided": worker_provided,
                "previewByteSize": preview_byte_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("jobId")

        task_type = d.pop("taskType")

        submitted_at = d.pop("submittedAt")

        worker_provided = d.pop("workerProvided")

        preview_byte_size = d.pop("previewByteSize")

        get_v1_jobs_job_id_preview_response_200_type_1_metadata = cls(
            job_id=job_id,
            task_type=task_type,
            submitted_at=submitted_at,
            worker_provided=worker_provided,
            preview_byte_size=preview_byte_size,
        )

        return get_v1_jobs_job_id_preview_response_200_type_1_metadata
