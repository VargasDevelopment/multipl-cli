from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_templates_response_200_item_capability_summary import (
        GetV1TemplatesResponse200ItemCapabilitySummary,
    )


T = TypeVar("T", bound="GetV1TemplatesResponse200Item")


@_attrs_define
class GetV1TemplatesResponse200Item:
    """
    Attributes:
        id (str):
        display_name (str):
        description (str):
        version (str):
        public (bool):
        stage_count (int):
        task_type_ids (list[str]):
        capability_summary (GetV1TemplatesResponse200ItemCapabilitySummary):
    """

    id: str
    display_name: str
    description: str
    version: str
    public: bool
    stage_count: int
    task_type_ids: list[str]
    capability_summary: GetV1TemplatesResponse200ItemCapabilitySummary

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        description = self.description

        version = self.version

        public = self.public

        stage_count = self.stage_count

        task_type_ids = self.task_type_ids

        capability_summary = self.capability_summary.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "displayName": display_name,
                "description": description,
                "version": version,
                "public": public,
                "stageCount": stage_count,
                "taskTypeIds": task_type_ids,
                "capabilitySummary": capability_summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_templates_response_200_item_capability_summary import (
            GetV1TemplatesResponse200ItemCapabilitySummary,
        )

        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("displayName")

        description = d.pop("description")

        version = d.pop("version")

        public = d.pop("public")

        stage_count = d.pop("stageCount")

        task_type_ids = cast(list[str], d.pop("taskTypeIds"))

        capability_summary = GetV1TemplatesResponse200ItemCapabilitySummary.from_dict(
            d.pop("capabilitySummary")
        )

        get_v1_templates_response_200_item = cls(
            id=id,
            display_name=display_name,
            description=description,
            version=version,
            public=public,
            stage_count=stage_count,
            task_type_ids=task_type_ids,
            capability_summary=capability_summary,
        )

        return get_v1_templates_response_200_item
