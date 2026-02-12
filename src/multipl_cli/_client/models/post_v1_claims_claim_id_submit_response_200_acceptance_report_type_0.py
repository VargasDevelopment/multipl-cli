from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_status import (
    PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Status,
)

if TYPE_CHECKING:
    from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_checks_item import (
        PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0ChecksItem,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_commitment import (
        PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Commitment,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_stats import (
        PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Stats,
    )


T = TypeVar("T", bound="PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0")


@_attrs_define
class PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0:
    """
    Attributes:
        version (str):
        status (PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Status):
        checks (list[PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0ChecksItem]):
        stats (PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Stats):
        commitment (PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Commitment):
    """

    version: str
    status: PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Status
    checks: list[PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0ChecksItem]
    stats: PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Stats
    commitment: PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Commitment

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
        from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_checks_item import (
            PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0ChecksItem,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_commitment import (
            PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Commitment,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0_stats import (
            PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Stats,
        )

        d = dict(src_dict)
        version = d.pop("version")

        status = PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Status(d.pop("status"))

        checks = []
        _checks = d.pop("checks")
        for checks_item_data in _checks:
            checks_item = (
                PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0ChecksItem.from_dict(
                    checks_item_data
                )
            )

            checks.append(checks_item)

        stats = PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Stats.from_dict(
            d.pop("stats")
        )

        commitment = PostV1ClaimsClaimIdSubmitResponse200AcceptanceReportType0Commitment.from_dict(
            d.pop("commitment")
        )

        post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0 = cls(
            version=version,
            status=status,
            checks=checks,
            stats=stats,
            commitment=commitment,
        )

        return post_v1_claims_claim_id_submit_response_200_acceptance_report_type_0
