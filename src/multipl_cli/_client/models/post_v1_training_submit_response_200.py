from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_training_submit_response_200_mode import PostV1TrainingSubmitResponse200Mode

if TYPE_CHECKING:
    from ..models.post_v1_training_submit_response_200_acceptance_report import (
        PostV1TrainingSubmitResponse200AcceptanceReport,
    )
    from ..models.post_v1_training_submit_response_200_diagnostics_item import (
        PostV1TrainingSubmitResponse200DiagnosticsItem,
    )


T = TypeVar("T", bound="PostV1TrainingSubmitResponse200")


@_attrs_define
class PostV1TrainingSubmitResponse200:
    """
    Attributes:
        mode (PostV1TrainingSubmitResponse200Mode):
        lease_id (str):
        exercise_id (str):
        pass_ (bool):
        acceptance_report (PostV1TrainingSubmitResponse200AcceptanceReport):
        diagnostics (list[PostV1TrainingSubmitResponse200DiagnosticsItem]):
    """

    mode: PostV1TrainingSubmitResponse200Mode
    lease_id: str
    exercise_id: str
    pass_: bool
    acceptance_report: PostV1TrainingSubmitResponse200AcceptanceReport
    diagnostics: list[PostV1TrainingSubmitResponse200DiagnosticsItem]

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        lease_id = self.lease_id

        exercise_id = self.exercise_id

        pass_ = self.pass_

        acceptance_report = self.acceptance_report.to_dict()

        diagnostics = []
        for diagnostics_item_data in self.diagnostics:
            diagnostics_item = diagnostics_item_data.to_dict()
            diagnostics.append(diagnostics_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
                "leaseId": lease_id,
                "exerciseId": exercise_id,
                "pass": pass_,
                "acceptanceReport": acceptance_report,
                "diagnostics": diagnostics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_training_submit_response_200_acceptance_report import (
            PostV1TrainingSubmitResponse200AcceptanceReport,
        )
        from ..models.post_v1_training_submit_response_200_diagnostics_item import (
            PostV1TrainingSubmitResponse200DiagnosticsItem,
        )

        d = dict(src_dict)
        mode = PostV1TrainingSubmitResponse200Mode(d.pop("mode"))

        lease_id = d.pop("leaseId")

        exercise_id = d.pop("exerciseId")

        pass_ = d.pop("pass")

        acceptance_report = PostV1TrainingSubmitResponse200AcceptanceReport.from_dict(
            d.pop("acceptanceReport")
        )

        diagnostics = []
        _diagnostics = d.pop("diagnostics")
        for diagnostics_item_data in _diagnostics:
            diagnostics_item = PostV1TrainingSubmitResponse200DiagnosticsItem.from_dict(
                diagnostics_item_data
            )

            diagnostics.append(diagnostics_item)

        post_v1_training_submit_response_200 = cls(
            mode=mode,
            lease_id=lease_id,
            exercise_id=exercise_id,
            pass_=pass_,
            acceptance_report=acceptance_report,
            diagnostics=diagnostics,
        )

        return post_v1_training_submit_response_200
