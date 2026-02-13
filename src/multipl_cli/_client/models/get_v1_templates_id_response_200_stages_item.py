from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_templates_id_response_200_stages_item_capabilities import (
        GetV1TemplatesIdResponse200StagesItemCapabilities,
    )


T = TypeVar("T", bound="GetV1TemplatesIdResponse200StagesItem")


@_attrs_define
class GetV1TemplatesIdResponse200StagesItem:
    """
    Attributes:
        index (int):
        title (str):
        task_type_id (str):
        prompt_template (str):
        capabilities (GetV1TemplatesIdResponse200StagesItemCapabilities):
        notes (str | Unset):
    """

    index: int
    title: str
    task_type_id: str
    prompt_template: str
    capabilities: GetV1TemplatesIdResponse200StagesItemCapabilities
    notes: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        index = self.index

        title = self.title

        task_type_id = self.task_type_id

        prompt_template = self.prompt_template

        capabilities = self.capabilities.to_dict()

        notes = self.notes

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "index": index,
                "title": title,
                "taskTypeId": task_type_id,
                "promptTemplate": prompt_template,
                "capabilities": capabilities,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_templates_id_response_200_stages_item_capabilities import (
            GetV1TemplatesIdResponse200StagesItemCapabilities,
        )

        d = dict(src_dict)
        index = d.pop("index")

        title = d.pop("title")

        task_type_id = d.pop("taskTypeId")

        prompt_template = d.pop("promptTemplate")

        capabilities = GetV1TemplatesIdResponse200StagesItemCapabilities.from_dict(
            d.pop("capabilities")
        )

        notes = d.pop("notes", UNSET)

        get_v1_templates_id_response_200_stages_item = cls(
            index=index,
            title=title,
            task_type_id=task_type_id,
            prompt_template=prompt_template,
            capabilities=capabilities,
            notes=notes,
        )

        return get_v1_templates_id_response_200_stages_item
