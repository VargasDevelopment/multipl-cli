from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_job_id_response_200_job_state import (
    GetV1PublicJobsJobIdResponse200JobState,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_job_acceptance_contract import (
        GetV1PublicJobsJobIdResponse200JobAcceptanceContract,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0 import (
        GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200Job")


@_attrs_define
class GetV1PublicJobsJobIdResponse200Job:
    """
    Attributes:
        id (str):
        task_type (str):
        state (GetV1PublicJobsJobIdResponse200JobState):
        payout_cents (int | None):
        requested_model (None | str):
        estimated_tokens (int | None):
        deadline_seconds (int | None):
        created_at (str):
        claimed_at (None | str):
        submitted_at (None | str):
        completed_at (None | str):
        is_platform_posted (bool):
        seed_batch (None | str):
        input_preview (None | str):
        acceptance_preview (None | str):
        acceptance_contract (GetV1PublicJobsJobIdResponse200JobAcceptanceContract):
        available_at (None | str):
        verification_policy (GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0 | None | Unset):
    """

    id: str
    task_type: str
    state: GetV1PublicJobsJobIdResponse200JobState
    payout_cents: int | None
    requested_model: None | str
    estimated_tokens: int | None
    deadline_seconds: int | None
    created_at: str
    claimed_at: None | str
    submitted_at: None | str
    completed_at: None | str
    is_platform_posted: bool
    seed_batch: None | str
    input_preview: None | str
    acceptance_preview: None | str
    acceptance_contract: GetV1PublicJobsJobIdResponse200JobAcceptanceContract
    available_at: None | str
    verification_policy: (
        GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0 | None | Unset
    ) = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0 import (
            GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0,
        )

        id = self.id

        task_type = self.task_type

        state = self.state.value

        payout_cents: int | None
        payout_cents = self.payout_cents

        requested_model: None | str
        requested_model = self.requested_model

        estimated_tokens: int | None
        estimated_tokens = self.estimated_tokens

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        created_at = self.created_at

        claimed_at: None | str
        claimed_at = self.claimed_at

        submitted_at: None | str
        submitted_at = self.submitted_at

        completed_at: None | str
        completed_at = self.completed_at

        is_platform_posted = self.is_platform_posted

        seed_batch: None | str
        seed_batch = self.seed_batch

        input_preview: None | str
        input_preview = self.input_preview

        acceptance_preview: None | str
        acceptance_preview = self.acceptance_preview

        acceptance_contract = self.acceptance_contract.to_dict()

        available_at: None | str
        available_at = self.available_at

        verification_policy: dict[str, Any] | None | Unset
        if isinstance(self.verification_policy, Unset):
            verification_policy = UNSET
        elif isinstance(
            self.verification_policy, GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0
        ):
            verification_policy = self.verification_policy.to_dict()
        else:
            verification_policy = self.verification_policy

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "taskType": task_type,
                "state": state,
                "payoutCents": payout_cents,
                "requestedModel": requested_model,
                "estimatedTokens": estimated_tokens,
                "deadlineSeconds": deadline_seconds,
                "createdAt": created_at,
                "claimedAt": claimed_at,
                "submittedAt": submitted_at,
                "completedAt": completed_at,
                "isPlatformPosted": is_platform_posted,
                "seedBatch": seed_batch,
                "inputPreview": input_preview,
                "acceptancePreview": acceptance_preview,
                "acceptanceContract": acceptance_contract,
                "availableAt": available_at,
            }
        )
        if verification_policy is not UNSET:
            field_dict["verificationPolicy"] = verification_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_job_acceptance_contract import (
            GetV1PublicJobsJobIdResponse200JobAcceptanceContract,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0 import (
            GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        task_type = d.pop("taskType")

        state = GetV1PublicJobsJobIdResponse200JobState(d.pop("state"))

        def _parse_payout_cents(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_cents = _parse_payout_cents(d.pop("payoutCents"))

        def _parse_requested_model(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        requested_model = _parse_requested_model(d.pop("requestedModel"))

        def _parse_estimated_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        estimated_tokens = _parse_estimated_tokens(d.pop("estimatedTokens"))

        def _parse_deadline_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        deadline_seconds = _parse_deadline_seconds(d.pop("deadlineSeconds"))

        created_at = d.pop("createdAt")

        def _parse_claimed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        claimed_at = _parse_claimed_at(d.pop("claimedAt"))

        def _parse_submitted_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        submitted_at = _parse_submitted_at(d.pop("submittedAt"))

        def _parse_completed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        completed_at = _parse_completed_at(d.pop("completedAt"))

        is_platform_posted = d.pop("isPlatformPosted")

        def _parse_seed_batch(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        seed_batch = _parse_seed_batch(d.pop("seedBatch"))

        def _parse_input_preview(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        input_preview = _parse_input_preview(d.pop("inputPreview"))

        def _parse_acceptance_preview(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        acceptance_preview = _parse_acceptance_preview(d.pop("acceptancePreview"))

        acceptance_contract = GetV1PublicJobsJobIdResponse200JobAcceptanceContract.from_dict(
            d.pop("acceptanceContract")
        )

        def _parse_available_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        available_at = _parse_available_at(d.pop("availableAt"))

        def _parse_verification_policy(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                verification_policy_type_0 = (
                    GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0.from_dict(data)
                )

                return verification_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0 | None | Unset, data
            )

        verification_policy = _parse_verification_policy(d.pop("verificationPolicy", UNSET))

        get_v1_public_jobs_job_id_response_200_job = cls(
            id=id,
            task_type=task_type,
            state=state,
            payout_cents=payout_cents,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            created_at=created_at,
            claimed_at=claimed_at,
            submitted_at=submitted_at,
            completed_at=completed_at,
            is_platform_posted=is_platform_posted,
            seed_batch=seed_batch,
            input_preview=input_preview,
            acceptance_preview=acceptance_preview,
            acceptance_contract=acceptance_contract,
            available_at=available_at,
            verification_policy=verification_policy,
        )

        return get_v1_public_jobs_job_id_response_200_job
