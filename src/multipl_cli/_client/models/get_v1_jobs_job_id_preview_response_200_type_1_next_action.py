from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_jobs_job_id_preview_response_200_type_1_next_action_endpoint import (
    GetV1JobsJobIdPreviewResponse200Type1NextActionEndpoint,
)
from ..models.get_v1_jobs_job_id_preview_response_200_type_1_next_action_kind import (
    GetV1JobsJobIdPreviewResponse200Type1NextActionKind,
)
from ..models.get_v1_jobs_job_id_preview_response_200_type_1_next_action_method import (
    GetV1JobsJobIdPreviewResponse200Type1NextActionMethod,
)

T = TypeVar("T", bound="GetV1JobsJobIdPreviewResponse200Type1NextAction")


@_attrs_define
class GetV1JobsJobIdPreviewResponse200Type1NextAction:
    """
    Attributes:
        kind (GetV1JobsJobIdPreviewResponse200Type1NextActionKind):
        endpoint (GetV1JobsJobIdPreviewResponse200Type1NextActionEndpoint):
        method (GetV1JobsJobIdPreviewResponse200Type1NextActionMethod):
        hint (str):
    """

    kind: GetV1JobsJobIdPreviewResponse200Type1NextActionKind
    endpoint: GetV1JobsJobIdPreviewResponse200Type1NextActionEndpoint
    method: GetV1JobsJobIdPreviewResponse200Type1NextActionMethod
    hint: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        endpoint = self.endpoint.value

        method = self.method.value

        hint = self.hint

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "endpoint": endpoint,
                "method": method,
                "hint": hint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = GetV1JobsJobIdPreviewResponse200Type1NextActionKind(d.pop("kind"))

        endpoint = GetV1JobsJobIdPreviewResponse200Type1NextActionEndpoint(d.pop("endpoint"))

        method = GetV1JobsJobIdPreviewResponse200Type1NextActionMethod(d.pop("method"))

        hint = d.pop("hint")

        get_v1_jobs_job_id_preview_response_200_type_1_next_action = cls(
            kind=kind,
            endpoint=endpoint,
            method=method,
            hint=hint,
        )

        return get_v1_jobs_job_id_preview_response_200_type_1_next_action
