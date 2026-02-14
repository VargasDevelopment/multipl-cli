from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_training_validate_job_response_200_mode import (
    PostV1TrainingValidateJobResponse200Mode,
)

if TYPE_CHECKING:
    from ..models.post_v1_training_validate_job_response_200_diagnostics_item import (
        PostV1TrainingValidateJobResponse200DiagnosticsItem,
    )


T = TypeVar("T", bound="PostV1TrainingValidateJobResponse200")


@_attrs_define
class PostV1TrainingValidateJobResponse200:
    """
    Attributes:
        mode (PostV1TrainingValidateJobResponse200Mode):
        pass_ (bool):
        diagnostics (list[PostV1TrainingValidateJobResponse200DiagnosticsItem]):
    """

    mode: PostV1TrainingValidateJobResponse200Mode
    pass_: bool
    diagnostics: list[PostV1TrainingValidateJobResponse200DiagnosticsItem]

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        pass_ = self.pass_

        diagnostics = []
        for diagnostics_item_data in self.diagnostics:
            diagnostics_item = diagnostics_item_data.to_dict()
            diagnostics.append(diagnostics_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
                "pass": pass_,
                "diagnostics": diagnostics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_validate_job_response_200_diagnostics_item import (
            PostV1TrainingValidateJobResponse200DiagnosticsItem,
        )

        d = dict(src_dict)
        mode = PostV1TrainingValidateJobResponse200Mode(d.pop("mode"))

        pass_ = d.pop("pass")

        diagnostics = []
        _diagnostics = d.pop("diagnostics")
        for diagnostics_item_data in _diagnostics:
            diagnostics_item = PostV1TrainingValidateJobResponse200DiagnosticsItem.from_dict(
                diagnostics_item_data
            )

            diagnostics.append(diagnostics_item)

        post_v1_training_validate_job_response_200 = cls(
            mode=mode,
            pass_=pass_,
            diagnostics=diagnostics,
        )

        return post_v1_training_validate_job_response_200
