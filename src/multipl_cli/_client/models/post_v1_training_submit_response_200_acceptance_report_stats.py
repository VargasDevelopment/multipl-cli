from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1TrainingSubmitResponse200AcceptanceReportStats")


@_attrs_define
class PostV1TrainingSubmitResponse200AcceptanceReportStats:
    """
    Attributes:
        bytes_ (int):
        top_level_keys (list[str] | Unset):
    """

    bytes_: int
    top_level_keys: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        bytes_ = self.bytes_

        top_level_keys: list[str] | Unset = UNSET
        if not isinstance(self.top_level_keys, Unset):
            top_level_keys = self.top_level_keys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "bytes": bytes_,
            }
        )
        if top_level_keys is not UNSET:
            field_dict["topLevelKeys"] = top_level_keys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bytes_ = d.pop("bytes")

        top_level_keys = cast(list[str], d.pop("topLevelKeys", UNSET))

        post_v1_training_submit_response_200_acceptance_report_stats = cls(
            bytes_=bytes_,
            top_level_keys=top_level_keys,
        )

        return post_v1_training_submit_response_200_acceptance_report_stats
