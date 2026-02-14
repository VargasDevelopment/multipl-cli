from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1TrainingSubmitResponse200DiagnosticsItem")


@_attrs_define
class PostV1TrainingSubmitResponse200DiagnosticsItem:
    """
    Attributes:
        code (str):
        message (str):
        path (str | Unset):
    """

    code: str
    message: str
    path: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        message = self.message

        path = self.path

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "code": code,
                "message": message,
            }
        )
        if path is not UNSET:
            field_dict["path"] = path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        path = d.pop("path", UNSET)

        post_v1_training_submit_response_200_diagnostics_item = cls(
            code=code,
            message=message,
            path=path,
        )

        return post_v1_training_submit_response_200_diagnostics_item
