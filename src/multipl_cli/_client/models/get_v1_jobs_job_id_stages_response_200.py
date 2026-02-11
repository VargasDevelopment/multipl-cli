from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_stages_response_200_stages_item import (
        GetV1JobsJobIdStagesResponse200StagesItem,
    )


T = TypeVar("T", bound="GetV1JobsJobIdStagesResponse200")


@_attrs_define
class GetV1JobsJobIdStagesResponse200:
    """
    Attributes:
        root_job_id (str):
        stages (list[GetV1JobsJobIdStagesResponse200StagesItem]):
    """

    root_job_id: str
    stages: list[GetV1JobsJobIdStagesResponse200StagesItem]

    def to_dict(self) -> dict[str, Any]:
        root_job_id = self.root_job_id

        stages = []
        for stages_item_data in self.stages:
            stages_item = stages_item_data.to_dict()
            stages.append(stages_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rootJobId": root_job_id,
                "stages": stages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_stages_response_200_stages_item import (
            GetV1JobsJobIdStagesResponse200StagesItem,
        )

        d = dict(src_dict)
        root_job_id = d.pop("rootJobId")

        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:
            stages_item = GetV1JobsJobIdStagesResponse200StagesItem.from_dict(stages_item_data)

            stages.append(stages_item)

        get_v1_jobs_job_id_stages_response_200 = cls(
            root_job_id=root_job_id,
            stages=stages,
        )

        return get_v1_jobs_job_id_stages_response_200
