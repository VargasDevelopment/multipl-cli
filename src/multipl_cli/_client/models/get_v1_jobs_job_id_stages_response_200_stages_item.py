from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_assignment_mode_type_0 import (
    GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0,
)
from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_state_type_0 import (
    GetV1JobsJobIdStagesResponse200StagesItemStateType0,
)
from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_state_type_1 import (
    GetV1JobsJobIdStagesResponse200StagesItemStateType1,
)
from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_visibility import (
    GetV1JobsJobIdStagesResponse200StagesItemVisibility,
)

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_proof_type_0 import (
        GetV1JobsJobIdStagesResponse200StagesItemProofType0,
    )


T = TypeVar("T", bound="GetV1JobsJobIdStagesResponse200StagesItem")


@_attrs_define
class GetV1JobsJobIdStagesResponse200StagesItem:
    """
    Attributes:
        root_job_id (str):
        stage_id (str):
        stage_index (int):
        name (None | str):
        task_type (str):
        visibility (GetV1JobsJobIdStagesResponse200StagesItemVisibility):
        assignment_mode (GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0 | None):
        reservation_seconds (int | None):
        state (GetV1JobsJobIdStagesResponse200StagesItemStateType0 |
            GetV1JobsJobIdStagesResponse200StagesItemStateType1):
        job_id (None | str):
        parent_job_id (None | str):
        payout_cents (int | None):
        deadline_seconds (int | None):
        reserved_worker_id (None | str):
        reserved_until (None | str):
        available_at (None | str):
        claimed_at (None | str):
        submitted_at (None | str):
        completed_at (None | str):
        paid_at (None | str):
        receipt_id (None | str):
        proof (GetV1JobsJobIdStagesResponse200StagesItemProofType0 | None):
    """

    root_job_id: str
    stage_id: str
    stage_index: int
    name: None | str
    task_type: str
    visibility: GetV1JobsJobIdStagesResponse200StagesItemVisibility
    assignment_mode: GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0 | None
    reservation_seconds: int | None
    state: (
        GetV1JobsJobIdStagesResponse200StagesItemStateType0
        | GetV1JobsJobIdStagesResponse200StagesItemStateType1
    )
    job_id: None | str
    parent_job_id: None | str
    payout_cents: int | None
    deadline_seconds: int | None
    reserved_worker_id: None | str
    reserved_until: None | str
    available_at: None | str
    claimed_at: None | str
    submitted_at: None | str
    completed_at: None | str
    paid_at: None | str
    receipt_id: None | str
    proof: GetV1JobsJobIdStagesResponse200StagesItemProofType0 | None

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_proof_type_0 import (
            GetV1JobsJobIdStagesResponse200StagesItemProofType0,
        )

        root_job_id = self.root_job_id

        stage_id = self.stage_id

        stage_index = self.stage_index

        name: None | str
        name = self.name

        task_type = self.task_type

        visibility = self.visibility.value

        assignment_mode: None | str
        if isinstance(
            self.assignment_mode, GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0
        ):
            assignment_mode = self.assignment_mode.value
        else:
            assignment_mode = self.assignment_mode

        reservation_seconds: int | None
        reservation_seconds = self.reservation_seconds

        state: str
        if isinstance(self.state, GetV1JobsJobIdStagesResponse200StagesItemStateType0):
            state = self.state.value
        else:
            state = self.state.value

        job_id: None | str
        job_id = self.job_id

        parent_job_id: None | str
        parent_job_id = self.parent_job_id

        payout_cents: int | None
        payout_cents = self.payout_cents

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        reserved_worker_id: None | str
        reserved_worker_id = self.reserved_worker_id

        reserved_until: None | str
        reserved_until = self.reserved_until

        available_at: None | str
        available_at = self.available_at

        claimed_at: None | str
        claimed_at = self.claimed_at

        submitted_at: None | str
        submitted_at = self.submitted_at

        completed_at: None | str
        completed_at = self.completed_at

        paid_at: None | str
        paid_at = self.paid_at

        receipt_id: None | str
        receipt_id = self.receipt_id

        proof: dict[str, Any] | None
        if isinstance(self.proof, GetV1JobsJobIdStagesResponse200StagesItemProofType0):
            proof = self.proof.to_dict()
        else:
            proof = self.proof

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rootJobId": root_job_id,
                "stageId": stage_id,
                "stageIndex": stage_index,
                "name": name,
                "taskType": task_type,
                "visibility": visibility,
                "assignmentMode": assignment_mode,
                "reservationSeconds": reservation_seconds,
                "state": state,
                "jobId": job_id,
                "parentJobId": parent_job_id,
                "payoutCents": payout_cents,
                "deadlineSeconds": deadline_seconds,
                "reservedWorkerId": reserved_worker_id,
                "reservedUntil": reserved_until,
                "availableAt": available_at,
                "claimedAt": claimed_at,
                "submittedAt": submitted_at,
                "completedAt": completed_at,
                "paidAt": paid_at,
                "receiptId": receipt_id,
                "proof": proof,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_stages_response_200_stages_item_proof_type_0 import (
            GetV1JobsJobIdStagesResponse200StagesItemProofType0,
        )

        d = dict(src_dict)
        root_job_id = d.pop("rootJobId")

        stage_id = d.pop("stageId")

        stage_index = d.pop("stageIndex")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        task_type = d.pop("taskType")

        visibility = GetV1JobsJobIdStagesResponse200StagesItemVisibility(d.pop("visibility"))

        def _parse_assignment_mode(
            data: object,
        ) -> GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                assignment_mode_type_0 = (
                    GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0(data)
                )

                return assignment_mode_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0 | None, data)

        assignment_mode = _parse_assignment_mode(d.pop("assignmentMode"))

        def _parse_reservation_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        reservation_seconds = _parse_reservation_seconds(d.pop("reservationSeconds"))

        def _parse_state(
            data: object,
        ) -> (
            GetV1JobsJobIdStagesResponse200StagesItemStateType0
            | GetV1JobsJobIdStagesResponse200StagesItemStateType1
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = GetV1JobsJobIdStagesResponse200StagesItemStateType0(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, str):
                raise TypeError()
            state_type_1 = GetV1JobsJobIdStagesResponse200StagesItemStateType1(data)

            return state_type_1

        state = _parse_state(d.pop("state"))

        def _parse_job_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        job_id = _parse_job_id(d.pop("jobId"))

        def _parse_parent_job_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_job_id = _parse_parent_job_id(d.pop("parentJobId"))

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

        def _parse_reserved_worker_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        reserved_worker_id = _parse_reserved_worker_id(d.pop("reservedWorkerId"))

        def _parse_reserved_until(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        reserved_until = _parse_reserved_until(d.pop("reservedUntil"))

        def _parse_available_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        available_at = _parse_available_at(d.pop("availableAt"))

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

        def _parse_paid_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        paid_at = _parse_paid_at(d.pop("paidAt"))

        def _parse_receipt_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        receipt_id = _parse_receipt_id(d.pop("receiptId"))

        def _parse_proof(
            data: object,
        ) -> GetV1JobsJobIdStagesResponse200StagesItemProofType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                proof_type_0 = GetV1JobsJobIdStagesResponse200StagesItemProofType0.from_dict(data)

                return proof_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsJobIdStagesResponse200StagesItemProofType0 | None, data)

        proof = _parse_proof(d.pop("proof"))

        get_v1_jobs_job_id_stages_response_200_stages_item = cls(
            root_job_id=root_job_id,
            stage_id=stage_id,
            stage_index=stage_index,
            name=name,
            task_type=task_type,
            visibility=visibility,
            assignment_mode=assignment_mode,
            reservation_seconds=reservation_seconds,
            state=state,
            job_id=job_id,
            parent_job_id=parent_job_id,
            payout_cents=payout_cents,
            deadline_seconds=deadline_seconds,
            reserved_worker_id=reserved_worker_id,
            reserved_until=reserved_until,
            available_at=available_at,
            claimed_at=claimed_at,
            submitted_at=submitted_at,
            completed_at=completed_at,
            paid_at=paid_at,
            receipt_id=receipt_id,
            proof=proof,
        )

        return get_v1_jobs_job_id_stages_response_200_stages_item
