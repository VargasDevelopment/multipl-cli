from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1WorkersMeResponse200ApiKey")


@_attrs_define
class GetV1WorkersMeResponse200ApiKey:
    """
    Attributes:
        id (str):
        prefix (str):
        created_at (str):
        last_used_at (None | str):
        revoked_at (None | str):
    """

    id: str
    prefix: str
    created_at: str
    last_used_at: None | str
    revoked_at: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        prefix = self.prefix

        created_at = self.created_at

        last_used_at: None | str
        last_used_at = self.last_used_at

        revoked_at: None | str
        revoked_at = self.revoked_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "prefix": prefix,
                "createdAt": created_at,
                "lastUsedAt": last_used_at,
                "revokedAt": revoked_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        prefix = d.pop("prefix")

        created_at = d.pop("createdAt")

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("lastUsedAt"))

        def _parse_revoked_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        revoked_at = _parse_revoked_at(d.pop("revokedAt"))

        get_v1_workers_me_response_200_api_key = cls(
            id=id,
            prefix=prefix,
            created_at=created_at,
            last_used_at=last_used_at,
            revoked_at=revoked_at,
        )

        return get_v1_workers_me_response_200_api_key
