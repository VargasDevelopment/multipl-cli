from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostV1WorkersClaimResponse200Worker")


@_attrs_define
class PostV1WorkersClaimResponse200Worker:
    """
    Attributes:
        id (str):
        name (str):
        is_claimed (bool):
        claimed_by_poster_id (None | str):
    """

    id: str
    name: str
    is_claimed: bool
    claimed_by_poster_id: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        is_claimed = self.is_claimed

        claimed_by_poster_id: None | str
        claimed_by_poster_id = self.claimed_by_poster_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "isClaimed": is_claimed,
                "claimedByPosterId": claimed_by_poster_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        is_claimed = d.pop("isClaimed")

        def _parse_claimed_by_poster_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        claimed_by_poster_id = _parse_claimed_by_poster_id(d.pop("claimedByPosterId"))

        post_v1_workers_claim_response_200_worker = cls(
            id=id,
            name=name,
            is_claimed=is_claimed,
            claimed_by_poster_id=claimed_by_poster_id,
        )

        return post_v1_workers_claim_response_200_worker
