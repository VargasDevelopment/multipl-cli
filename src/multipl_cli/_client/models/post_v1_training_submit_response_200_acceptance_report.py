from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_training_submit_response_200_acceptance_report_status import (
    PostV1TrainingSubmitResponse200AcceptanceReportStatus,
)

if TYPE_CHECKING:
    from ..models.post_v1_training_submit_response_200_acceptance_report_checks_item import (
        PostV1TrainingSubmitResponse200AcceptanceReportChecksItem,
    )
    from ..models.post_v1_training_submit_response_200_acceptance_report_commitment import (
        PostV1TrainingSubmitResponse200AcceptanceReportCommitment,
    )
    from ..models.post_v1_training_submit_response_200_acceptance_report_stats import (
        PostV1TrainingSubmitResponse200AcceptanceReportStats,
    )


T = TypeVar("T", bound="PostV1TrainingSubmitResponse200AcceptanceReport")


@_attrs_define
class PostV1TrainingSubmitResponse200AcceptanceReport:
    """
    Attributes:
        version (str):
        status (PostV1TrainingSubmitResponse200AcceptanceReportStatus):
        checks (list[PostV1TrainingSubmitResponse200AcceptanceReportChecksItem]):
        stats (PostV1TrainingSubmitResponse200AcceptanceReportStats):
        commitment (PostV1TrainingSubmitResponse200AcceptanceReportCommitment):
    """

    version: str
    status: PostV1TrainingSubmitResponse200AcceptanceReportStatus
    checks: list[PostV1TrainingSubmitResponse200AcceptanceReportChecksItem]
    stats: PostV1TrainingSubmitResponse200AcceptanceReportStats
    commitment: PostV1TrainingSubmitResponse200AcceptanceReportCommitment

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
        from ..models.post_v1_training_submit_response_200_acceptance_report_checks_item import (
            PostV1TrainingSubmitResponse200AcceptanceReportChecksItem,
        )
        from ..models.post_v1_training_submit_response_200_acceptance_report_commitment import (
            PostV1TrainingSubmitResponse200AcceptanceReportCommitment,
        )
        from ..models.post_v1_training_submit_response_200_acceptance_report_stats import (
            PostV1TrainingSubmitResponse200AcceptanceReportStats,
        )

        d = dict(src_dict)
        version = d.pop("version")

        status = PostV1TrainingSubmitResponse200AcceptanceReportStatus(d.pop("status"))

        checks = []
        _checks = d.pop("checks")
        for checks_item_data in _checks:
            checks_item = PostV1TrainingSubmitResponse200AcceptanceReportChecksItem.from_dict(
                checks_item_data
            )

            checks.append(checks_item)

        stats = PostV1TrainingSubmitResponse200AcceptanceReportStats.from_dict(d.pop("stats"))

        commitment = PostV1TrainingSubmitResponse200AcceptanceReportCommitment.from_dict(
            d.pop("commitment")
        )

        post_v1_training_submit_response_200_acceptance_report = cls(
            version=version,
            status=status,
            checks=checks,
            stats=stats,
            commitment=commitment,
        )

        return post_v1_training_submit_response_200_acceptance_report
