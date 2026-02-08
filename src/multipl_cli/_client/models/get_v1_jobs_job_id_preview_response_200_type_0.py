from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_jobs_job_id_preview_response_200_type_0_reason import (
    GetV1JobsJobIdPreviewResponse200Type0Reason,
)

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_preview_response_200_type_0_metadata import (
        GetV1JobsJobIdPreviewResponse200Type0Metadata,
    )


T = TypeVar("T", bound="GetV1JobsJobIdPreviewResponse200Type0")


@_attrs_define
class GetV1JobsJobIdPreviewResponse200Type0:
    """
    Attributes:
        blocked (bool):
        reason (GetV1JobsJobIdPreviewResponse200Type0Reason):
        metadata (GetV1JobsJobIdPreviewResponse200Type0Metadata):
    """

    blocked: bool
    reason: GetV1JobsJobIdPreviewResponse200Type0Reason
    metadata: GetV1JobsJobIdPreviewResponse200Type0Metadata

    def to_dict(self) -> dict[str, Any]:
        blocked = self.blocked

        reason = self.reason.value

        metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "blocked": blocked,
                "reason": reason,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_preview_response_200_type_0_metadata import (
            GetV1JobsJobIdPreviewResponse200Type0Metadata,
        )

        d = dict(src_dict)
        blocked = d.pop("blocked")

        reason = GetV1JobsJobIdPreviewResponse200Type0Reason(d.pop("reason"))

        metadata = GetV1JobsJobIdPreviewResponse200Type0Metadata.from_dict(d.pop("metadata"))

        get_v1_jobs_job_id_preview_response_200_type_0 = cls(
            blocked=blocked,
            reason=reason,
            metadata=metadata,
        )

        return get_v1_jobs_job_id_preview_response_200_type_0
