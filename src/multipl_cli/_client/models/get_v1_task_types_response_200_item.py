from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_task_types_response_200_item_role import GetV1TaskTypesResponse200ItemRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_task_types_response_200_item_acceptance_defaults import (
        GetV1TaskTypesResponse200ItemAcceptanceDefaults,
    )


T = TypeVar("T", bound="GetV1TaskTypesResponse200Item")


@_attrs_define
class GetV1TaskTypesResponse200Item:
    """
    Attributes:
        id (str):
        display_name (str):
        role (GetV1TaskTypesResponse200ItemRole):
        public (bool):
        aliases (list[str] | Unset):
        acceptance_defaults (GetV1TaskTypesResponse200ItemAcceptanceDefaults | Unset):
    """

    id: str
    display_name: str
    role: GetV1TaskTypesResponse200ItemRole
    public: bool
    aliases: list[str] | Unset = UNSET
    acceptance_defaults: GetV1TaskTypesResponse200ItemAcceptanceDefaults | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        role = self.role.value

        public = self.public

        aliases: list[str] | Unset = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = self.aliases

        acceptance_defaults: dict[str, Any] | Unset = UNSET
        if not isinstance(self.acceptance_defaults, Unset):
            acceptance_defaults = self.acceptance_defaults.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "displayName": display_name,
                "role": role,
                "public": public,
            }
        )
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if acceptance_defaults is not UNSET:
            field_dict["acceptanceDefaults"] = acceptance_defaults

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_task_types_response_200_item_acceptance_defaults import (
            GetV1TaskTypesResponse200ItemAcceptanceDefaults,
        )

        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("displayName")

        role = GetV1TaskTypesResponse200ItemRole(d.pop("role"))

        public = d.pop("public")

        aliases = cast(list[str], d.pop("aliases", UNSET))

        _acceptance_defaults = d.pop("acceptanceDefaults", UNSET)
        acceptance_defaults: GetV1TaskTypesResponse200ItemAcceptanceDefaults | Unset
        if isinstance(_acceptance_defaults, Unset):
            acceptance_defaults = UNSET
        else:
            acceptance_defaults = GetV1TaskTypesResponse200ItemAcceptanceDefaults.from_dict(
                _acceptance_defaults
            )

        get_v1_task_types_response_200_item = cls(
            id=id,
            display_name=display_name,
            role=role,
            public=public,
            aliases=aliases,
            acceptance_defaults=acceptance_defaults,
        )

        return get_v1_task_types_response_200_item
