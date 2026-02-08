from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_preview_response_200_type_1_acceptance_report_type_0 import (
        GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0,
    )
    from ..models.get_v1_jobs_job_id_preview_response_200_type_1_metadata import (
        GetV1JobsJobIdPreviewResponse200Type1Metadata,
    )
    from ..models.get_v1_jobs_job_id_preview_response_200_type_1_next_action import (
        GetV1JobsJobIdPreviewResponse200Type1NextAction,
    )


T = TypeVar("T", bound="GetV1JobsJobIdPreviewResponse200Type1")


@_attrs_define
class GetV1JobsJobIdPreviewResponse200Type1:
    """
    Attributes:
        payment_required (bool):
        commitment_sha_256 (str):
        acceptance_report (GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0 | None):
        metadata (GetV1JobsJobIdPreviewResponse200Type1Metadata):
        preview_json (Any | None | Unset):
        next_action (GetV1JobsJobIdPreviewResponse200Type1NextAction | Unset):
    """

    payment_required: bool
    commitment_sha_256: str
    acceptance_report: GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0 | None
    metadata: GetV1JobsJobIdPreviewResponse200Type1Metadata
    preview_json: Any | None | Unset = UNSET
    next_action: GetV1JobsJobIdPreviewResponse200Type1NextAction | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_jobs_job_id_preview_response_200_type_1_acceptance_report_type_0 import (
            GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0,
        )

        payment_required = self.payment_required

        commitment_sha_256 = self.commitment_sha_256

        acceptance_report: dict[str, Any] | None
        if isinstance(
            self.acceptance_report, GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0
        ):
            acceptance_report = self.acceptance_report.to_dict()
        else:
            acceptance_report = self.acceptance_report

        metadata = self.metadata.to_dict()

        preview_json: Any | None | Unset
        if isinstance(self.preview_json, Unset):
            preview_json = UNSET
        else:
            preview_json = self.preview_json

        next_action: dict[str, Any] | Unset = UNSET
        if not isinstance(self.next_action, Unset):
            next_action = self.next_action.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "paymentRequired": payment_required,
                "commitmentSha256": commitment_sha_256,
                "acceptanceReport": acceptance_report,
                "metadata": metadata,
            }
        )
        if preview_json is not UNSET:
            field_dict["previewJson"] = preview_json
        if next_action is not UNSET:
            field_dict["nextAction"] = next_action

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_preview_response_200_type_1_acceptance_report_type_0 import (
            GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0,
        )
        from ..models.get_v1_jobs_job_id_preview_response_200_type_1_metadata import (
            GetV1JobsJobIdPreviewResponse200Type1Metadata,
        )
        from ..models.get_v1_jobs_job_id_preview_response_200_type_1_next_action import (
            GetV1JobsJobIdPreviewResponse200Type1NextAction,
        )

        d = dict(src_dict)
        payment_required = d.pop("paymentRequired")

        commitment_sha_256 = d.pop("commitmentSha256")

        def _parse_acceptance_report(
            data: object,
        ) -> GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                acceptance_report_type_0 = (
                    GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0.from_dict(data)
                )

                return acceptance_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsJobIdPreviewResponse200Type1AcceptanceReportType0 | None, data)

        acceptance_report = _parse_acceptance_report(d.pop("acceptanceReport"))

        metadata = GetV1JobsJobIdPreviewResponse200Type1Metadata.from_dict(d.pop("metadata"))

        def _parse_preview_json(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        preview_json = _parse_preview_json(d.pop("previewJson", UNSET))

        _next_action = d.pop("nextAction", UNSET)
        next_action: GetV1JobsJobIdPreviewResponse200Type1NextAction | Unset
        if isinstance(_next_action, Unset):
            next_action = UNSET
        else:
            next_action = GetV1JobsJobIdPreviewResponse200Type1NextAction.from_dict(_next_action)

        get_v1_jobs_job_id_preview_response_200_type_1 = cls(
            payment_required=payment_required,
            commitment_sha_256=commitment_sha_256,
            acceptance_report=acceptance_report,
            metadata=metadata,
            preview_json=preview_json,
            next_action=next_action,
        )

        return get_v1_jobs_job_id_preview_response_200_type_1
