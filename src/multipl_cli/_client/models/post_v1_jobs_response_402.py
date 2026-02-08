from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_v1_jobs_response_402_error import PostV1JobsResponse402Error
from ..models.post_v1_jobs_response_402_kind import PostV1JobsResponse402Kind
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostV1JobsResponse402")


@_attrs_define
class PostV1JobsResponse402:
    """
    Attributes:
        error (PostV1JobsResponse402Error):
        kind (PostV1JobsResponse402Kind):
        recipient (str):
        amount (int):
        asset (str):
        network (str):
        payment_context (str):
        facilitator (str | Unset):
        platform_fee_cents (int | Unset):
        hint (str | Unset):
    """

    error: PostV1JobsResponse402Error
    kind: PostV1JobsResponse402Kind
    recipient: str
    amount: int
    asset: str
    network: str
    payment_context: str
    facilitator: str | Unset = UNSET
    platform_fee_cents: int | Unset = UNSET
    hint: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        kind = self.kind.value

        recipient = self.recipient

        amount = self.amount

        asset = self.asset

        network = self.network

        payment_context = self.payment_context

        facilitator = self.facilitator

        platform_fee_cents = self.platform_fee_cents

        hint = self.hint

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
                "kind": kind,
                "recipient": recipient,
                "amount": amount,
                "asset": asset,
                "network": network,
                "payment_context": payment_context,
            }
        )
        if facilitator is not UNSET:
            field_dict["facilitator"] = facilitator
        if platform_fee_cents is not UNSET:
            field_dict["platform_fee_cents"] = platform_fee_cents
        if hint is not UNSET:
            field_dict["hint"] = hint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = PostV1JobsResponse402Error(d.pop("error"))

        kind = PostV1JobsResponse402Kind(d.pop("kind"))

        recipient = d.pop("recipient")

        amount = d.pop("amount")

        asset = d.pop("asset")

        network = d.pop("network")

        payment_context = d.pop("payment_context")

        facilitator = d.pop("facilitator", UNSET)

        platform_fee_cents = d.pop("platform_fee_cents", UNSET)

        hint = d.pop("hint", UNSET)

        post_v1_jobs_response_402 = cls(
            error=error,
            kind=kind,
            recipient=recipient,
            amount=amount,
            asset=asset,
            network=network,
            payment_context=payment_context,
            facilitator=facilitator,
            platform_fee_cents=platform_fee_cents,
            hint=hint,
        )

        return post_v1_jobs_response_402
