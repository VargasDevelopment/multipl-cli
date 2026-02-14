from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1TrainingSubmitBody")


@_attrs_define
class PostV1TrainingSubmitBody:
    """
    Attributes:
        lease_id (str):
        submit_token (str):
        output (Any | Unset):
    """

    lease_id: str
    submit_token: str
    output: Any | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        lease_id = self.lease_id

        submit_token = self.submit_token

        output = self.output

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "leaseId": lease_id,
                "submitToken": submit_token,
            }
        )
        if output is not UNSET:
            field_dict["output"] = output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lease_id = d.pop("leaseId")

        submit_token = d.pop("submitToken")

        output = d.pop("output", UNSET)

        post_v1_training_submit_body = cls(
            lease_id=lease_id,
            submit_token=submit_token,
            output=output,
        )

        return post_v1_training_submit_body
