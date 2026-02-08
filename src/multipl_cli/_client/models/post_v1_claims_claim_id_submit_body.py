from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1ClaimsClaimIdSubmitBody")


@_attrs_define
class PostV1ClaimsClaimIdSubmitBody:
    """
    Attributes:
        output (Any | Unset):
        preview (Any | Unset):
        model_used (str | Unset):
        tokens_used (int | Unset):
    """

    output: Any | Unset = UNSET
    preview: Any | Unset = UNSET
    model_used: str | Unset = UNSET
    tokens_used: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        output = self.output

        preview = self.preview

        model_used = self.model_used

        tokens_used = self.tokens_used

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if output is not UNSET:
            field_dict["output"] = output
        if preview is not UNSET:
            field_dict["preview"] = preview
        if model_used is not UNSET:
            field_dict["modelUsed"] = model_used
        if tokens_used is not UNSET:
            field_dict["tokensUsed"] = tokens_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        output = d.pop("output", UNSET)

        preview = d.pop("preview", UNSET)

        model_used = d.pop("modelUsed", UNSET)

        tokens_used = d.pop("tokensUsed", UNSET)

        post_v1_claims_claim_id_submit_body = cls(
            output=output,
            preview=preview,
            model_used=model_used,
            tokens_used=tokens_used,
        )

        return post_v1_claims_claim_id_submit_body
