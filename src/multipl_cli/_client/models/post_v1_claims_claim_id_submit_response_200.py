from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0 import (
        PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_job import (
        PostV1ClaimsClaimIdSubmitResponse200Job,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_submission import (
        PostV1ClaimsClaimIdSubmitResponse200Submission,
    )


T = TypeVar("T", bound="PostV1ClaimsClaimIdSubmitResponse200")


@_attrs_define
class PostV1ClaimsClaimIdSubmitResponse200:
    """
    Attributes:
        submission (PostV1ClaimsClaimIdSubmitResponse200Submission):
        job (PostV1ClaimsClaimIdSubmitResponse200Job):
        acceptance_report (None | PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0):
    """

    submission: PostV1ClaimsClaimIdSubmitResponse200Submission
    job: PostV1ClaimsClaimIdSubmitResponse200Job
    acceptance_report: None | PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0

    def to_dict(self) -> dict[str, Any]:
        from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0,
        )

        submission = self.submission.to_dict()

        job = self.job.to_dict()

        acceptance_report: dict[str, Any] | None
        if isinstance(
            self.acceptance_report, PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0
        ):
            acceptance_report = self.acceptance_report.to_dict()
        else:
            acceptance_report = self.acceptance_report

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "submission": submission,
                "job": job,
                "acceptanceReport": acceptance_report,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_job import (
            PostV1ClaimsClaimIdSubmitResponse200Job,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_submission import (
            PostV1ClaimsClaimIdSubmitResponse200Submission,
        )

        d = dict(src_dict)
        submission = PostV1ClaimsClaimIdSubmitResponse200Submission.from_dict(d.pop("submission"))

        job = PostV1ClaimsClaimIdSubmitResponse200Job.from_dict(d.pop("job"))

        def _parse_acceptance_report(
            data: object,
        ) -> None | PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                acceptance_report_type_0 = (
                    PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0.from_dict(data)
                )

                return acceptance_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0, data)

        acceptance_report = _parse_acceptance_report(d.pop("acceptanceReport"))

        post_v1_claims_claim_id_submit_response_200 = cls(
            submission=submission,
            job=job,
            acceptance_report=acceptance_report,
        )

        return post_v1_claims_claim_id_submit_response_200
