from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_templates_id_response_200_capability_summary import (
        GetV1TemplatesIdResponse200CapabilitySummary,
    )
    from ..models.get_v1_templates_id_response_200_defaults import (
        GetV1TemplatesIdResponse200Defaults,
    )
    from ..models.get_v1_templates_id_response_200_examples_item import (
        GetV1TemplatesIdResponse200ExamplesItem,
    )
    from ..models.get_v1_templates_id_response_200_input_schema import (
        GetV1TemplatesIdResponse200InputSchema,
    )
    from ..models.get_v1_templates_id_response_200_stages_item import (
        GetV1TemplatesIdResponse200StagesItem,
    )


T = TypeVar("T", bound="GetV1TemplatesIdResponse200")


@_attrs_define
class GetV1TemplatesIdResponse200:
    """
    Attributes:
        id (str):
        display_name (str):
        description (str):
        version (str):
        public (bool):
        stage_count (int):
        task_type_ids (list[str]):
        capability_summary (GetV1TemplatesIdResponse200CapabilitySummary):
        input_schema (GetV1TemplatesIdResponse200InputSchema):
        stages (list[GetV1TemplatesIdResponse200StagesItem]):
        defaults (GetV1TemplatesIdResponse200Defaults | Unset):
        examples (list[GetV1TemplatesIdResponse200ExamplesItem] | Unset):
    """

    id: str
    display_name: str
    description: str
    version: str
    public: bool
    stage_count: int
    task_type_ids: list[str]
    capability_summary: GetV1TemplatesIdResponse200CapabilitySummary
    input_schema: GetV1TemplatesIdResponse200InputSchema
    stages: list[GetV1TemplatesIdResponse200StagesItem]
    defaults: GetV1TemplatesIdResponse200Defaults | Unset = UNSET
    examples: list[GetV1TemplatesIdResponse200ExamplesItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        description = self.description

        version = self.version

        public = self.public

        stage_count = self.stage_count

        task_type_ids = self.task_type_ids

        capability_summary = self.capability_summary.to_dict()

        input_schema = self.input_schema.to_dict()

        stages = []
        for stages_item_data in self.stages:
            stages_item = stages_item_data.to_dict()
            stages.append(stages_item)

        defaults: dict[str, Any] | Unset = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        examples: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.examples, Unset):
            examples = []
            for examples_item_data in self.examples:
                examples_item = examples_item_data.to_dict()
                examples.append(examples_item)

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
                "inputSchema": input_schema,
                "stages": stages,
            }
        )
        if defaults is not UNSET:
            field_dict["defaults"] = defaults
        if examples is not UNSET:
            field_dict["examples"] = examples

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_templates_id_response_200_capability_summary import (
            GetV1TemplatesIdResponse200CapabilitySummary,
        )
        from ..models.get_v1_templates_id_response_200_defaults import (
            GetV1TemplatesIdResponse200Defaults,
        )
        from ..models.get_v1_templates_id_response_200_examples_item import (
            GetV1TemplatesIdResponse200ExamplesItem,
        )
        from ..models.get_v1_templates_id_response_200_input_schema import (
            GetV1TemplatesIdResponse200InputSchema,
        )
        from ..models.get_v1_templates_id_response_200_stages_item import (
            GetV1TemplatesIdResponse200StagesItem,
        )

        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("displayName")

        description = d.pop("description")

        version = d.pop("version")

        public = d.pop("public")

        stage_count = d.pop("stageCount")

        task_type_ids = cast(list[str], d.pop("taskTypeIds"))

        capability_summary = GetV1TemplatesIdResponse200CapabilitySummary.from_dict(
            d.pop("capabilitySummary")
        )

        input_schema = GetV1TemplatesIdResponse200InputSchema.from_dict(d.pop("inputSchema"))

        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:
            stages_item = GetV1TemplatesIdResponse200StagesItem.from_dict(stages_item_data)

            stages.append(stages_item)

        _defaults = d.pop("defaults", UNSET)
        defaults: GetV1TemplatesIdResponse200Defaults | Unset
        if isinstance(_defaults, Unset):
            defaults = UNSET
        else:
            defaults = GetV1TemplatesIdResponse200Defaults.from_dict(_defaults)

        _examples = d.pop("examples", UNSET)
        examples: list[GetV1TemplatesIdResponse200ExamplesItem] | Unset = UNSET
        if _examples is not UNSET:
            examples = []
            for examples_item_data in _examples:
                examples_item = GetV1TemplatesIdResponse200ExamplesItem.from_dict(
                    examples_item_data
                )

                examples.append(examples_item)

        get_v1_templates_id_response_200 = cls(
            id=id,
            display_name=display_name,
            description=description,
            version=version,
            public=public,
            stage_count=stage_count,
            task_type_ids=task_type_ids,
            capability_summary=capability_summary,
            input_schema=input_schema,
            stages=stages,
            defaults=defaults,
            examples=examples,
        )

        return get_v1_templates_id_response_200
