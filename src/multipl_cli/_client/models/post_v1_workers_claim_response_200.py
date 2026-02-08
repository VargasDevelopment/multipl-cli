from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_workers_claim_response_200_worker import (
        PostV1WorkersClaimResponse200Worker,
    )


T = TypeVar("T", bound="PostV1WorkersClaimResponse200")


@_attrs_define
class PostV1WorkersClaimResponse200:
    """
    Attributes:
        ok (bool):
        worker (PostV1WorkersClaimResponse200Worker):
    """

    ok: bool
    worker: PostV1WorkersClaimResponse200Worker

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        worker = self.worker.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "worker": worker,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_workers_claim_response_200_worker import (
            PostV1WorkersClaimResponse200Worker,
        )

        d = dict(src_dict)
        ok = d.pop("ok")

        worker = PostV1WorkersClaimResponse200Worker.from_dict(d.pop("worker"))

        post_v1_workers_claim_response_200 = cls(
            ok=ok,
            worker=worker,
        )

        return post_v1_workers_claim_response_200
