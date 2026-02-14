from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1TrainingSubmitResponse200AcceptanceReportChecksItem")


@_attrs_define
class PostV1TrainingSubmitResponse200AcceptanceReportChecksItem:
    """
    Attributes:
        name (str):
        passed (bool):
        reason (str | Unset):
        details (Any | Unset):
    """

    name: str
    passed: bool
    reason: str | Unset = UNSET
    details: Any | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        passed = self.passed

        reason = self.reason

        details = self.details

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "passed": passed,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        passed = d.pop("passed")

        reason = d.pop("reason", UNSET)

        details = d.pop("details", UNSET)

        post_v1_training_submit_response_200_acceptance_report_checks_item = cls(
            name=name,
            passed=passed,
            reason=reason,
            details=details,
        )

        return post_v1_training_submit_response_200_acceptance_report_checks_item
