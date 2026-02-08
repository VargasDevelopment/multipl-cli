from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_job import (
        GetV1PublicJobsJobIdResponse200Job,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_results import (
        GetV1PublicJobsJobIdResponse200Results,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_submission_summary_type_0 import (
        GetV1PublicJobsJobIdResponse200SubmissionSummaryType0,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verification import (
        GetV1PublicJobsJobIdResponse200Verification,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context import (
        GetV1PublicJobsJobIdResponse200VerifierContext,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200")


@_attrs_define
class GetV1PublicJobsJobIdResponse200:
    """
    Attributes:
        job (GetV1PublicJobsJobIdResponse200Job):
        submission_summary (GetV1PublicJobsJobIdResponse200SubmissionSummaryType0 | None):
        results (GetV1PublicJobsJobIdResponse200Results):
        verification (GetV1PublicJobsJobIdResponse200Verification | Unset):
        verifier_context (GetV1PublicJobsJobIdResponse200VerifierContext | Unset):
    """

    job: GetV1PublicJobsJobIdResponse200Job
    submission_summary: GetV1PublicJobsJobIdResponse200SubmissionSummaryType0 | None
    results: GetV1PublicJobsJobIdResponse200Results
    verification: GetV1PublicJobsJobIdResponse200Verification | Unset = UNSET
    verifier_context: GetV1PublicJobsJobIdResponse200VerifierContext | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_submission_summary_type_0 import (
            GetV1PublicJobsJobIdResponse200SubmissionSummaryType0,
        )

        job = self.job.to_dict()

        submission_summary: dict[str, Any] | None
        if isinstance(
            self.submission_summary, GetV1PublicJobsJobIdResponse200SubmissionSummaryType0
        ):
            submission_summary = self.submission_summary.to_dict()
        else:
            submission_summary = self.submission_summary

        results = self.results.to_dict()

        verification: dict[str, Any] | Unset = UNSET
        if not isinstance(self.verification, Unset):
            verification = self.verification.to_dict()

        verifier_context: dict[str, Any] | Unset = UNSET
        if not isinstance(self.verifier_context, Unset):
            verifier_context = self.verifier_context.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "job": job,
                "submissionSummary": submission_summary,
                "results": results,
            }
        )
        if verification is not UNSET:
            field_dict["verification"] = verification
        if verifier_context is not UNSET:
            field_dict["verifierContext"] = verifier_context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_job import (
            GetV1PublicJobsJobIdResponse200Job,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_results import (
            GetV1PublicJobsJobIdResponse200Results,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_submission_summary_type_0 import (
            GetV1PublicJobsJobIdResponse200SubmissionSummaryType0,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verification import (
            GetV1PublicJobsJobIdResponse200Verification,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context import (
            GetV1PublicJobsJobIdResponse200VerifierContext,
        )

        d = dict(src_dict)
        job = GetV1PublicJobsJobIdResponse200Job.from_dict(d.pop("job"))

        def _parse_submission_summary(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200SubmissionSummaryType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                submission_summary_type_0 = (
                    GetV1PublicJobsJobIdResponse200SubmissionSummaryType0.from_dict(data)
                )

                return submission_summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1PublicJobsJobIdResponse200SubmissionSummaryType0 | None, data)

        submission_summary = _parse_submission_summary(d.pop("submissionSummary"))

        results = GetV1PublicJobsJobIdResponse200Results.from_dict(d.pop("results"))

        _verification = d.pop("verification", UNSET)
        verification: GetV1PublicJobsJobIdResponse200Verification | Unset
        if isinstance(_verification, Unset):
            verification = UNSET
        else:
            verification = GetV1PublicJobsJobIdResponse200Verification.from_dict(_verification)

        _verifier_context = d.pop("verifierContext", UNSET)
        verifier_context: GetV1PublicJobsJobIdResponse200VerifierContext | Unset
        if isinstance(_verifier_context, Unset):
            verifier_context = UNSET
        else:
            verifier_context = GetV1PublicJobsJobIdResponse200VerifierContext.from_dict(
                _verifier_context
            )

        get_v1_public_jobs_job_id_response_200 = cls(
            job=job,
            submission_summary=submission_summary,
            results=results,
            verification=verification,
            verifier_context=verifier_context,
        )

        return get_v1_public_jobs_job_id_response_200
