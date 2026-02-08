from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_job_id_response_200_verification_jobs_item_state import (
    GetV1PublicJobsJobIdResponse200VerificationJobsItemState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200VerificationJobsItem")


@_attrs_define
class GetV1PublicJobsJobIdResponse200VerificationJobsItem:
    """
    Attributes:
        id (str):
        task_type (str):
        state (GetV1PublicJobsJobIdResponse200VerificationJobsItemState):
        payout_cents (int | None):
        deadline_seconds (int | None):
        created_at (str):
        claimed_at (None | str):
        submitted_at (None | str):
        completed_at (None | str):
        verifier_id_suffix (None | str):
        report_sha_256 (None | str):
        report_preview (Any | None | Unset):
    """

    id: str
    task_type: str
    state: GetV1PublicJobsJobIdResponse200VerificationJobsItemState
    payout_cents: int | None
    deadline_seconds: int | None
    created_at: str
    claimed_at: None | str
    submitted_at: None | str
    completed_at: None | str
    verifier_id_suffix: None | str
    report_sha_256: None | str
    report_preview: Any | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        task_type = self.task_type

        state = self.state.value

        payout_cents: int | None
        payout_cents = self.payout_cents

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        created_at = self.created_at

        claimed_at: None | str
        claimed_at = self.claimed_at

        submitted_at: None | str
        submitted_at = self.submitted_at

        completed_at: None | str
        completed_at = self.completed_at

        verifier_id_suffix: None | str
        verifier_id_suffix = self.verifier_id_suffix

        report_sha_256: None | str
        report_sha_256 = self.report_sha_256

        report_preview: Any | None | Unset
        if isinstance(self.report_preview, Unset):
            report_preview = UNSET
        else:
            report_preview = self.report_preview

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "taskType": task_type,
                "state": state,
                "payoutCents": payout_cents,
                "deadlineSeconds": deadline_seconds,
                "createdAt": created_at,
                "claimedAt": claimed_at,
                "submittedAt": submitted_at,
                "completedAt": completed_at,
                "verifierIdSuffix": verifier_id_suffix,
                "reportSha256": report_sha_256,
            }
        )
        if report_preview is not UNSET:
            field_dict["reportPreview"] = report_preview

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        task_type = d.pop("taskType")

        state = GetV1PublicJobsJobIdResponse200VerificationJobsItemState(d.pop("state"))

        def _parse_payout_cents(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_cents = _parse_payout_cents(d.pop("payoutCents"))

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

        def _parse_verifier_id_suffix(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        verifier_id_suffix = _parse_verifier_id_suffix(d.pop("verifierIdSuffix"))

        def _parse_report_sha_256(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        report_sha_256 = _parse_report_sha_256(d.pop("reportSha256"))

        def _parse_report_preview(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        report_preview = _parse_report_preview(d.pop("reportPreview", UNSET))

        get_v1_public_jobs_job_id_response_200_verification_jobs_item = cls(
            id=id,
            task_type=task_type,
            state=state,
            payout_cents=payout_cents,
            deadline_seconds=deadline_seconds,
            created_at=created_at,
            claimed_at=claimed_at,
            submitted_at=submitted_at,
            completed_at=completed_at,
            verifier_id_suffix=verifier_id_suffix,
            report_sha_256=report_sha_256,
            report_preview=report_preview,
        )

        return get_v1_public_jobs_job_id_response_200_verification_jobs_item
