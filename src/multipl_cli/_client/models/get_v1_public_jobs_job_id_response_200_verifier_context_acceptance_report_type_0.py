from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_status import (
    GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Status,
)

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_checks_item import (
        GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0ChecksItem,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_commitment import (
        GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Commitment,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_stats import (
        GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Stats,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0")


@_attrs_define
class GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0:
    """
    Attributes:
        version (str):
        status (GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Status):
        checks (list[GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0ChecksItem]):
        stats (GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Stats):
        commitment (GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Commitment):
    """

    version: str
    status: GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Status
    checks: list[GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0ChecksItem]
    stats: GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Stats
    commitment: GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Commitment

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        status = self.status.value

        checks = []
        for checks_item_data in self.checks:
            checks_item = checks_item_data.to_dict()
            checks.append(checks_item)

        stats = self.stats.to_dict()

        commitment = self.commitment.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "version": version,
                "status": status,
                "checks": checks,
                "stats": stats,
                "commitment": commitment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_checks_item import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0ChecksItem,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_commitment import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Commitment,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0_stats import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Stats,
        )

        d = dict(src_dict)
        version = d.pop("version")

        status = GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Status(
            d.pop("status")
        )

        checks = []
        _checks = d.pop("checks")
        for checks_item_data in _checks:
            checks_item = GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0ChecksItem.from_dict(
                checks_item_data
            )

            checks.append(checks_item)

        stats = GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Stats.from_dict(
            d.pop("stats")
        )

        commitment = (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Commitment.from_dict(
                d.pop("commitment")
            )
        )

        get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0 = cls(
            version=version,
            status=status,
            checks=checks,
            stats=stats,
            commitment=commitment,
        )

        return get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0
