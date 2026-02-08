from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200SubmissionSummaryType0")


@_attrs_define
class GetV1PublicJobsJobIdResponse200SubmissionSummaryType0:
    """
    Attributes:
        submission_id (str):
        worker_id_suffix (None | str):
        created_at (str):
        artifact_sha_256 (None | str):
        artifact_expires_at (None | str):
    """

    submission_id: str
    worker_id_suffix: None | str
    created_at: str
    artifact_sha_256: None | str
    artifact_expires_at: None | str

    def to_dict(self) -> dict[str, Any]:
        submission_id = self.submission_id

        worker_id_suffix: None | str
        worker_id_suffix = self.worker_id_suffix

        created_at = self.created_at

        artifact_sha_256: None | str
        artifact_sha_256 = self.artifact_sha_256

        artifact_expires_at: None | str
        artifact_expires_at = self.artifact_expires_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "submissionId": submission_id,
                "workerIdSuffix": worker_id_suffix,
                "createdAt": created_at,
                "artifactSha256": artifact_sha_256,
                "artifactExpiresAt": artifact_expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        submission_id = d.pop("submissionId")

        def _parse_worker_id_suffix(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        worker_id_suffix = _parse_worker_id_suffix(d.pop("workerIdSuffix"))

        created_at = d.pop("createdAt")

        def _parse_artifact_sha_256(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        artifact_sha_256 = _parse_artifact_sha_256(d.pop("artifactSha256"))

        def _parse_artifact_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        artifact_expires_at = _parse_artifact_expires_at(d.pop("artifactExpiresAt"))

        get_v1_public_jobs_job_id_response_200_submission_summary_type_0 = cls(
            submission_id=submission_id,
            worker_id_suffix=worker_id_suffix,
            created_at=created_at,
            artifact_sha_256=artifact_sha_256,
            artifact_expires_at=artifact_expires_at,
        )

        return get_v1_public_jobs_job_id_response_200_submission_summary_type_0
