from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_workers_me_response_200_worker_metadata_type_0_type_1 import (
        GetV1WorkersMeResponse200WorkerMetadataType0Type1,
    )


T = TypeVar("T", bound="GetV1WorkersMeResponse200Worker")


@_attrs_define
class GetV1WorkersMeResponse200Worker:
    """
    Attributes:
        id (str):
        name (str):
        description (None | str):
        is_claimed (bool):
        claimed_by_poster_id (None | str):
        metadata (Any | GetV1WorkersMeResponse200WorkerMetadataType0Type1 | None | Unset):
    """

    id: str
    name: str
    description: None | str
    is_claimed: bool
    claimed_by_poster_id: None | str
    metadata: Any | GetV1WorkersMeResponse200WorkerMetadataType0Type1 | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_workers_me_response_200_worker_metadata_type_0_type_1 import (
            GetV1WorkersMeResponse200WorkerMetadataType0Type1,
        )

        id = self.id

        name = self.name

        description: None | str
        description = self.description

        is_claimed = self.is_claimed

        claimed_by_poster_id: None | str
        claimed_by_poster_id = self.claimed_by_poster_id

        metadata: Any | dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, GetV1WorkersMeResponse200WorkerMetadataType0Type1):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "isClaimed": is_claimed,
                "claimedByPosterId": claimed_by_poster_id,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_workers_me_response_200_worker_metadata_type_0_type_1 import (
            GetV1WorkersMeResponse200WorkerMetadataType0Type1,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        is_claimed = d.pop("isClaimed")

        def _parse_claimed_by_poster_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        claimed_by_poster_id = _parse_claimed_by_poster_id(d.pop("claimedByPosterId"))

        def _parse_metadata(
            data: object,
        ) -> Any | GetV1WorkersMeResponse200WorkerMetadataType0Type1 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0_type_1 = (
                    GetV1WorkersMeResponse200WorkerMetadataType0Type1.from_dict(data)
                )

                return metadata_type_0_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Any | GetV1WorkersMeResponse200WorkerMetadataType0Type1 | None | Unset, data
            )

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        get_v1_workers_me_response_200_worker = cls(
            id=id,
            name=name,
            description=description,
            is_claimed=is_claimed,
            claimed_by_poster_id=claimed_by_poster_id,
            metadata=metadata,
        )

        return get_v1_workers_me_response_200_worker
