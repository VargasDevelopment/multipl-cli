from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_workers_me_response_200_api_key import GetV1WorkersMeResponse200ApiKey
    from ..models.get_v1_workers_me_response_200_worker import GetV1WorkersMeResponse200Worker


T = TypeVar("T", bound="GetV1WorkersMeResponse200")


@_attrs_define
class GetV1WorkersMeResponse200:
    """
    Attributes:
        worker (GetV1WorkersMeResponse200Worker):
        api_key (GetV1WorkersMeResponse200ApiKey):
    """

    worker: GetV1WorkersMeResponse200Worker
    api_key: GetV1WorkersMeResponse200ApiKey

    def to_dict(self) -> dict[str, Any]:
        worker = self.worker.to_dict()

        api_key = self.api_key.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "worker": worker,
                "api_key": api_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_workers_me_response_200_api_key import GetV1WorkersMeResponse200ApiKey
        from ..models.get_v1_workers_me_response_200_worker import GetV1WorkersMeResponse200Worker

        d = dict(src_dict)
        worker = GetV1WorkersMeResponse200Worker.from_dict(d.pop("worker"))

        api_key = GetV1WorkersMeResponse200ApiKey.from_dict(d.pop("api_key"))

        get_v1_workers_me_response_200 = cls(
            worker=worker,
            api_key=api_key,
        )

        return get_v1_workers_me_response_200
