from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_task_types_response_200_item_acceptance_defaults_must_include import (
        GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude,
    )
    from ..models.get_v1_task_types_response_200_item_acceptance_defaults_output_schema import (
        GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema,
    )


T = TypeVar("T", bound="GetV1TaskTypesResponse200ItemAcceptanceDefaults")


@_attrs_define
class GetV1TaskTypesResponse200ItemAcceptanceDefaults:
    """
    Attributes:
        max_bytes (int | Unset):
        must_include (GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude | Unset):
        output_schema (GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema | Unset):
        deterministic_checks (list[str] | Unset):
    """

    max_bytes: int | Unset = UNSET
    must_include: GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude | Unset = UNSET
    output_schema: GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema | Unset = UNSET
    deterministic_checks: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        max_bytes = self.max_bytes

        must_include: dict[str, Any] | Unset = UNSET
        if not isinstance(self.must_include, Unset):
            must_include = self.must_include.to_dict()

        output_schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.output_schema, Unset):
            output_schema = self.output_schema.to_dict()

        deterministic_checks: list[str] | Unset = UNSET
        if not isinstance(self.deterministic_checks, Unset):
            deterministic_checks = self.deterministic_checks

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if max_bytes is not UNSET:
            field_dict["maxBytes"] = max_bytes
        if must_include is not UNSET:
            field_dict["mustInclude"] = must_include
        if output_schema is not UNSET:
            field_dict["outputSchema"] = output_schema
        if deterministic_checks is not UNSET:
            field_dict["deterministicChecks"] = deterministic_checks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_task_types_response_200_item_acceptance_defaults_must_include import (
            GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude,
        )
        from ..models.get_v1_task_types_response_200_item_acceptance_defaults_output_schema import (
            GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema,
        )

        d = dict(src_dict)
        max_bytes = d.pop("maxBytes", UNSET)

        _must_include = d.pop("mustInclude", UNSET)
        must_include: GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude | Unset
        if isinstance(_must_include, Unset):
            must_include = UNSET
        else:
            must_include = GetV1TaskTypesResponse200ItemAcceptanceDefaultsMustInclude.from_dict(
                _must_include
            )

        _output_schema = d.pop("outputSchema", UNSET)
        output_schema: GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema | Unset
        if isinstance(_output_schema, Unset):
            output_schema = UNSET
        else:
            output_schema = GetV1TaskTypesResponse200ItemAcceptanceDefaultsOutputSchema.from_dict(
                _output_schema
            )

        deterministic_checks = cast(list[str], d.pop("deterministicChecks", UNSET))

        get_v1_task_types_response_200_item_acceptance_defaults = cls(
            max_bytes=max_bytes,
            must_include=must_include,
            output_schema=output_schema,
            deterministic_checks=deterministic_checks,
        )

        return get_v1_task_types_response_200_item_acceptance_defaults
