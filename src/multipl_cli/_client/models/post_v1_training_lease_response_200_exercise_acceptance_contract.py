from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract_must_include import (
        PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude,
    )
    from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract_output_schema import (
        PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema,
    )


T = TypeVar("T", bound="PostV1TrainingLeaseResponse200ExerciseAcceptanceContract")


@_attrs_define
class PostV1TrainingLeaseResponse200ExerciseAcceptanceContract:
    """
    Attributes:
        max_bytes (int | Unset):
        must_include (PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude | Unset):
        output_schema (PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema | Unset):
        deterministic_checks (list[str] | Unset):
    """

    max_bytes: int | Unset = UNSET
    must_include: PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude | Unset = (
        UNSET
    )
    output_schema: PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema | Unset = (
        UNSET
    )
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
        from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract_must_include import (
            PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude,
        )
        from ..models.post_v1_training_lease_response_200_exercise_acceptance_contract_output_schema import (
            PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema,
        )

        d = dict(src_dict)
        max_bytes = d.pop("maxBytes", UNSET)

        _must_include = d.pop("mustInclude", UNSET)
        must_include: PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude | Unset
        if isinstance(_must_include, Unset):
            must_include = UNSET
        else:
            must_include = (
                PostV1TrainingLeaseResponse200ExerciseAcceptanceContractMustInclude.from_dict(
                    _must_include
                )
            )

        _output_schema = d.pop("outputSchema", UNSET)
        output_schema: PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema | Unset
        if isinstance(_output_schema, Unset):
            output_schema = UNSET
        else:
            output_schema = (
                PostV1TrainingLeaseResponse200ExerciseAcceptanceContractOutputSchema.from_dict(
                    _output_schema
                )
            )

        deterministic_checks = cast(list[str], d.pop("deterministicChecks", UNSET))

        post_v1_training_lease_response_200_exercise_acceptance_contract = cls(
            max_bytes=max_bytes,
            must_include=must_include,
            output_schema=output_schema,
            deterministic_checks=deterministic_checks,
        )

        return post_v1_training_lease_response_200_exercise_acceptance_contract
