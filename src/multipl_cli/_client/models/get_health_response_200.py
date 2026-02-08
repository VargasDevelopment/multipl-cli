from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetHealthResponse200")


@_attrs_define
class GetHealthResponse200:
    """
    Attributes:
        ok (bool):
        db (bool):
        redis (bool):
    """

    ok: bool
    db: bool
    redis: bool

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        db = self.db

        redis = self.redis

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "db": db,
                "redis": redis,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ok = d.pop("ok")

        db = d.pop("db")

        redis = d.pop("redis")

        get_health_response_200 = cls(
            ok=ok,
            db=db,
            redis=redis,
        )

        return get_health_response_200
