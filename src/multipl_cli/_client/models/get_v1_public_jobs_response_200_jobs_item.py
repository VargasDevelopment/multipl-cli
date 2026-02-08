from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_response_200_jobs_item_state import (
    GetV1PublicJobsResponse200JobsItemState,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust import (
        GetV1PublicJobsResponse200JobsItemPosterTrust,
    )
    from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust import (
        GetV1PublicJobsResponse200JobsItemWorkerTrust,
    )


T = TypeVar("T", bound="GetV1PublicJobsResponse200JobsItem")


@_attrs_define
class GetV1PublicJobsResponse200JobsItem:
    """
    Attributes:
        id (str):
        task_type (str):
        state (GetV1PublicJobsResponse200JobsItemState):
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
        poster_trust (GetV1PublicJobsResponse200JobsItemPosterTrust):
        worker_trust (GetV1PublicJobsResponse200JobsItemWorkerTrust | Unset):
    """

    id: str
    task_type: str
    state: GetV1PublicJobsResponse200JobsItemState
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
    poster_trust: GetV1PublicJobsResponse200JobsItemPosterTrust
    worker_trust: GetV1PublicJobsResponse200JobsItemWorkerTrust | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
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

        poster_trust = self.poster_trust.to_dict()

        worker_trust: dict[str, Any] | Unset = UNSET
        if not isinstance(self.worker_trust, Unset):
            worker_trust = self.worker_trust.to_dict()

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
                "posterTrust": poster_trust,
            }
        )
        if worker_trust is not UNSET:
            field_dict["workerTrust"] = worker_trust

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust import (
            GetV1PublicJobsResponse200JobsItemPosterTrust,
        )
        from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust import (
            GetV1PublicJobsResponse200JobsItemWorkerTrust,
        )

        d = dict(src_dict)
        id = d.pop("id")

        task_type = d.pop("taskType")

        state = GetV1PublicJobsResponse200JobsItemState(d.pop("state"))

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

        poster_trust = GetV1PublicJobsResponse200JobsItemPosterTrust.from_dict(d.pop("posterTrust"))

        _worker_trust = d.pop("workerTrust", UNSET)
        worker_trust: GetV1PublicJobsResponse200JobsItemWorkerTrust | Unset
        if isinstance(_worker_trust, Unset):
            worker_trust = UNSET
        else:
            worker_trust = GetV1PublicJobsResponse200JobsItemWorkerTrust.from_dict(_worker_trust)

        get_v1_public_jobs_response_200_jobs_item = cls(
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
            poster_trust=poster_trust,
            worker_trust=worker_trust,
        )

        return get_v1_public_jobs_response_200_jobs_item
