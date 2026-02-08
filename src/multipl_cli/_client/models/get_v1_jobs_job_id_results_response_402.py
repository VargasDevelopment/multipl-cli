from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_jobs_job_id_results_response_402_error import (
    GetV1JobsJobIdResultsResponse402Error,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_results_response_402_acceptance_report_type_0 import (
        GetV1JobsJobIdResultsResponse402AcceptanceReportType0,
    )
    from ..models.get_v1_jobs_job_id_results_response_402_metadata import (
        GetV1JobsJobIdResultsResponse402Metadata,
    )


T = TypeVar("T", bound="GetV1JobsJobIdResultsResponse402")


@_attrs_define
class GetV1JobsJobIdResultsResponse402:
    """
    Attributes:
        error (GetV1JobsJobIdResultsResponse402Error):
        recipient (str):
        amount (int):
        asset (str):
        network (str):
        payment_context (str):
        commitment_sha_256 (str):
        acceptance_report (GetV1JobsJobIdResultsResponse402AcceptanceReportType0 | None):
        metadata (GetV1JobsJobIdResultsResponse402Metadata):
        facilitator (str | Unset):
        hint (str | Unset):
        preview_json (Any | None | Unset):
    """

    error: GetV1JobsJobIdResultsResponse402Error
    recipient: str
    amount: int
    asset: str
    network: str
    payment_context: str
    commitment_sha_256: str
    acceptance_report: GetV1JobsJobIdResultsResponse402AcceptanceReportType0 | None
    metadata: GetV1JobsJobIdResultsResponse402Metadata
    facilitator: str | Unset = UNSET
    hint: str | Unset = UNSET
    preview_json: Any | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_jobs_job_id_results_response_402_acceptance_report_type_0 import (
            GetV1JobsJobIdResultsResponse402AcceptanceReportType0,
        )

        error = self.error.value

        recipient = self.recipient

        amount = self.amount

        asset = self.asset

        network = self.network

        payment_context = self.payment_context

        commitment_sha_256 = self.commitment_sha_256

        acceptance_report: dict[str, Any] | None
        if isinstance(
            self.acceptance_report, GetV1JobsJobIdResultsResponse402AcceptanceReportType0
        ):
            acceptance_report = self.acceptance_report.to_dict()
        else:
            acceptance_report = self.acceptance_report

        metadata = self.metadata.to_dict()

        facilitator = self.facilitator

        hint = self.hint

        preview_json: Any | None | Unset
        if isinstance(self.preview_json, Unset):
            preview_json = UNSET
        else:
            preview_json = self.preview_json

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
                "recipient": recipient,
                "amount": amount,
                "asset": asset,
                "network": network,
                "payment_context": payment_context,
                "commitmentSha256": commitment_sha_256,
                "acceptanceReport": acceptance_report,
                "metadata": metadata,
            }
        )
        if facilitator is not UNSET:
            field_dict["facilitator"] = facilitator
        if hint is not UNSET:
            field_dict["hint"] = hint
        if preview_json is not UNSET:
            field_dict["previewJson"] = preview_json

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_results_response_402_acceptance_report_type_0 import (
            GetV1JobsJobIdResultsResponse402AcceptanceReportType0,
        )
        from ..models.get_v1_jobs_job_id_results_response_402_metadata import (
            GetV1JobsJobIdResultsResponse402Metadata,
        )

        d = dict(src_dict)
        error = GetV1JobsJobIdResultsResponse402Error(d.pop("error"))

        recipient = d.pop("recipient")

        amount = d.pop("amount")

        asset = d.pop("asset")

        network = d.pop("network")

        payment_context = d.pop("payment_context")

        commitment_sha_256 = d.pop("commitmentSha256")

        def _parse_acceptance_report(
            data: object,
        ) -> GetV1JobsJobIdResultsResponse402AcceptanceReportType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                acceptance_report_type_0 = (
                    GetV1JobsJobIdResultsResponse402AcceptanceReportType0.from_dict(data)
                )

                return acceptance_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsJobIdResultsResponse402AcceptanceReportType0 | None, data)

        acceptance_report = _parse_acceptance_report(d.pop("acceptanceReport"))

        metadata = GetV1JobsJobIdResultsResponse402Metadata.from_dict(d.pop("metadata"))

        facilitator = d.pop("facilitator", UNSET)

        hint = d.pop("hint", UNSET)

        def _parse_preview_json(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        preview_json = _parse_preview_json(d.pop("previewJson", UNSET))

        get_v1_jobs_job_id_results_response_402 = cls(
            error=error,
            recipient=recipient,
            amount=amount,
            asset=asset,
            network=network,
            payment_context=payment_context,
            commitment_sha_256=commitment_sha_256,
            acceptance_report=acceptance_report,
            metadata=metadata,
            facilitator=facilitator,
            hint=hint,
            preview_json=preview_json,
        )

        return get_v1_jobs_job_id_results_response_402
