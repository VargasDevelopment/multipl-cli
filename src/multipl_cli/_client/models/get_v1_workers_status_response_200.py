from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_workers_status_response_200_status import GetV1WorkersStatusResponse200Status
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetV1WorkersStatusResponse200")


@_attrs_define
class GetV1WorkersStatusResponse200:
    """
    Attributes:
        status (GetV1WorkersStatusResponse200Status):
        claimed_by_poster_id (str | Unset):
    """

    status: GetV1WorkersStatusResponse200Status
    claimed_by_poster_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        claimed_by_poster_id = self.claimed_by_poster_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
            }
        )
        if claimed_by_poster_id is not UNSET:
            field_dict["claimedByPosterId"] = claimed_by_poster_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = GetV1WorkersStatusResponse200Status(d.pop("status"))

        claimed_by_poster_id = d.pop("claimedByPosterId", UNSET)

        get_v1_workers_status_response_200 = cls(
            status=status,
            claimed_by_poster_id=claimed_by_poster_id,
        )

        return get_v1_workers_status_response_200
