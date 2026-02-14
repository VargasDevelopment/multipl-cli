from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="PostV1TrainingSubmitResponse200AcceptanceReportCommitment")


@_attrs_define
class PostV1TrainingSubmitResponse200AcceptanceReportCommitment:
    """
    Attributes:
        sha256 (str):
        computed_at (datetime.datetime):
    """

    sha256: str
    computed_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        sha256 = self.sha256

        computed_at = self.computed_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sha256": sha256,
                "computedAt": computed_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sha256 = d.pop("sha256")

        computed_at = isoparse(d.pop("computedAt"))

        post_v1_training_submit_response_200_acceptance_report_commitment = cls(
            sha256=sha256,
            computed_at=computed_at,
        )

        return post_v1_training_submit_response_200_acceptance_report_commitment
