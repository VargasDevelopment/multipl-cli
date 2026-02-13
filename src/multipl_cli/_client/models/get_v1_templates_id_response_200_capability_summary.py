from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1TemplatesIdResponse200CapabilitySummary")


@_attrs_define
class GetV1TemplatesIdResponse200CapabilitySummary:
    """
    Attributes:
        requires_network (bool):
        requires_git (bool):
        allows_side_effects (bool):
    """

    requires_network: bool
    requires_git: bool
    allows_side_effects: bool

    def to_dict(self) -> dict[str, Any]:
        requires_network = self.requires_network

        requires_git = self.requires_git

        allows_side_effects = self.allows_side_effects

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "requiresNetwork": requires_network,
                "requiresGit": requires_git,
                "allowsSideEffects": allows_side_effects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        requires_network = d.pop("requiresNetwork")

        requires_git = d.pop("requiresGit")

        allows_side_effects = d.pop("allowsSideEffects")

        get_v1_templates_id_response_200_capability_summary = cls(
            requires_network=requires_network,
            requires_git=requires_git,
            allows_side_effects=allows_side_effects,
        )

        return get_v1_templates_id_response_200_capability_summary
