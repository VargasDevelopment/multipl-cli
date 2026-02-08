from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_results_response_200_result_acceptance_report_type_0 import (
        GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0,
    )


T = TypeVar("T", bound="GetV1JobsJobIdResultsResponse200Result")


@_attrs_define
class GetV1JobsJobIdResultsResponse200Result:
    """
    Attributes:
        job_id (str):
        submission_id (None | str):
        worker_id (str):
        sha256 (str):
        commitment_sha_256 (str):
        acceptance_report (GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0 | None):
        created_at (str):
        expires_at (None | str):
        payload (Any | Unset):
    """

    job_id: str
    submission_id: None | str
    worker_id: str
    sha256: str
    commitment_sha_256: str
    acceptance_report: GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0 | None
    created_at: str
    expires_at: None | str
    payload: Any | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_jobs_job_id_results_response_200_result_acceptance_report_type_0 import (
            GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0,
        )

        job_id = self.job_id

        submission_id: None | str
        submission_id = self.submission_id

        worker_id = self.worker_id

        sha256 = self.sha256

        commitment_sha_256 = self.commitment_sha_256

        acceptance_report: dict[str, Any] | None
        if isinstance(
            self.acceptance_report, GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0
        ):
            acceptance_report = self.acceptance_report.to_dict()
        else:
            acceptance_report = self.acceptance_report

        created_at = self.created_at

        expires_at: None | str
        expires_at = self.expires_at

        payload = self.payload

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobId": job_id,
                "submissionId": submission_id,
                "workerId": worker_id,
                "sha256": sha256,
                "commitmentSha256": commitment_sha_256,
                "acceptanceReport": acceptance_report,
                "createdAt": created_at,
                "expiresAt": expires_at,
            }
        )
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_results_response_200_result_acceptance_report_type_0 import (
            GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0,
        )

        d = dict(src_dict)
        job_id = d.pop("jobId")

        def _parse_submission_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        submission_id = _parse_submission_id(d.pop("submissionId"))

        worker_id = d.pop("workerId")

        sha256 = d.pop("sha256")

        commitment_sha_256 = d.pop("commitmentSha256")

        def _parse_acceptance_report(
            data: object,
        ) -> GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                acceptance_report_type_0 = (
                    GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0.from_dict(data)
                )

                return acceptance_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsJobIdResultsResponse200ResultAcceptanceReportType0 | None, data)

        acceptance_report = _parse_acceptance_report(d.pop("acceptanceReport"))

        created_at = d.pop("createdAt")

        def _parse_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        expires_at = _parse_expires_at(d.pop("expiresAt"))

        payload = d.pop("payload", UNSET)

        get_v1_jobs_job_id_results_response_200_result = cls(
            job_id=job_id,
            submission_id=submission_id,
            worker_id=worker_id,
            sha256=sha256,
            commitment_sha_256=commitment_sha_256,
            acceptance_report=acceptance_report,
            created_at=created_at,
            expires_at=expires_at,
            payload=payload,
        )

        return get_v1_jobs_job_id_results_response_200_result
