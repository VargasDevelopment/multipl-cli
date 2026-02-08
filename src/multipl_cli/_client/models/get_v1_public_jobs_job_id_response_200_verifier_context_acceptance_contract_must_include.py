from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar(
    "T", bound="GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContractMustInclude"
)


@_attrs_define
class GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContractMustInclude:
    """
    Attributes:
        keys (list[str] | Unset):
        substrings (list[str] | Unset):
    """

    keys: list[str] | Unset = UNSET
    substrings: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        keys: list[str] | Unset = UNSET
        if not isinstance(self.keys, Unset):
            keys = self.keys

        substrings: list[str] | Unset = UNSET
        if not isinstance(self.substrings, Unset):
            substrings = self.substrings

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if keys is not UNSET:
            field_dict["keys"] = keys
        if substrings is not UNSET:
            field_dict["substrings"] = substrings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        keys = cast(list[str], d.pop("keys", UNSET))

        substrings = cast(list[str], d.pop("substrings", UNSET))

        get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_contract_must_include = (
            cls(
                keys=keys,
                substrings=substrings,
            )
        )

        return (
            get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_contract_must_include
        )
