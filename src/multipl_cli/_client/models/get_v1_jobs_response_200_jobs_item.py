from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_jobs_response_200_jobs_item_state import GetV1JobsResponse200JobsItemState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_jobs_response_200_jobs_item_rubric_type_0 import (
        GetV1JobsResponse200JobsItemRubricType0,
    )


T = TypeVar("T", bound="GetV1JobsResponse200JobsItem")


@_attrs_define
class GetV1JobsResponse200JobsItem:
    """
    Attributes:
        id (str):
        task_type (str):
        state (GetV1JobsResponse200JobsItemState):
        payout_cents (int | None):
        deadline_seconds (int | None):
        created_at (str):
        expires_at (str):
        parent_job_id (None | str):
        parent_submission_id (None | str):
        rubric (GetV1JobsResponse200JobsItemRubricType0 | None | str | Unset):
    """

    id: str
    task_type: str
    state: GetV1JobsResponse200JobsItemState
    payout_cents: int | None
    deadline_seconds: int | None
    created_at: str
    expires_at: str
    parent_job_id: None | str
    parent_submission_id: None | str
    rubric: GetV1JobsResponse200JobsItemRubricType0 | None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_jobs_response_200_jobs_item_rubric_type_0 import (
            GetV1JobsResponse200JobsItemRubricType0,
        )

        id = self.id

        task_type = self.task_type

        state = self.state.value

        payout_cents: int | None
        payout_cents = self.payout_cents

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        created_at = self.created_at

        expires_at = self.expires_at

        parent_job_id: None | str
        parent_job_id = self.parent_job_id

        parent_submission_id: None | str
        parent_submission_id = self.parent_submission_id

        rubric: dict[str, Any] | None | str | Unset
        if isinstance(self.rubric, Unset):
            rubric = UNSET
        elif isinstance(self.rubric, GetV1JobsResponse200JobsItemRubricType0):
            rubric = self.rubric.to_dict()
        else:
            rubric = self.rubric

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "taskType": task_type,
                "state": state,
                "payoutCents": payout_cents,
                "deadlineSeconds": deadline_seconds,
                "createdAt": created_at,
                "expiresAt": expires_at,
                "parentJobId": parent_job_id,
                "parentSubmissionId": parent_submission_id,
            }
        )
        if rubric is not UNSET:
            field_dict["rubric"] = rubric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_response_200_jobs_item_rubric_type_0 import (
            GetV1JobsResponse200JobsItemRubricType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        task_type = d.pop("taskType")

        state = GetV1JobsResponse200JobsItemState(d.pop("state"))

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

        expires_at = d.pop("expiresAt")

        def _parse_parent_job_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_job_id = _parse_parent_job_id(d.pop("parentJobId"))

        def _parse_parent_submission_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_submission_id = _parse_parent_submission_id(d.pop("parentSubmissionId"))

        def _parse_rubric(
            data: object,
        ) -> GetV1JobsResponse200JobsItemRubricType0 | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rubric_type_0 = GetV1JobsResponse200JobsItemRubricType0.from_dict(data)

                return rubric_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1JobsResponse200JobsItemRubricType0 | None | str | Unset, data)

        rubric = _parse_rubric(d.pop("rubric", UNSET))

        get_v1_jobs_response_200_jobs_item = cls(
            id=id,
            task_type=task_type,
            state=state,
            payout_cents=payout_cents,
            deadline_seconds=deadline_seconds,
            created_at=created_at,
            expires_at=expires_at,
            parent_job_id=parent_job_id,
            parent_submission_id=parent_submission_id,
            rubric=rubric,
        )

        return get_v1_jobs_response_200_jobs_item
