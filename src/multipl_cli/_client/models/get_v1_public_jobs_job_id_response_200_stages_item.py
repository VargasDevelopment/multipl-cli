from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_job_id_response_200_stages_item_state_type_0 import (
    GetV1PublicJobsJobIdResponse200StagesItemStateType0,
)
from ..models.get_v1_public_jobs_job_id_response_200_stages_item_state_type_1 import (
    GetV1PublicJobsJobIdResponse200StagesItemStateType1,
)
from ..models.get_v1_public_jobs_job_id_response_200_stages_item_visibility import (
    GetV1PublicJobsJobIdResponse200StagesItemVisibility,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_stages_item_public_proof_type_0 import (
        GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200StagesItem")


@_attrs_define
class GetV1PublicJobsJobIdResponse200StagesItem:
    """
    Attributes:
        stage_id (str):
        stage_index (int):
        name (None | str):
        task_type (str):
        visibility (GetV1PublicJobsJobIdResponse200StagesItemVisibility):
        state (GetV1PublicJobsJobIdResponse200StagesItemStateType0 |
            GetV1PublicJobsJobIdResponse200StagesItemStateType1):
        payout_cents (int | None):
        is_unlocked (bool):
        public_proof (GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0 | None | Unset):
    """

    stage_id: str
    stage_index: int
    name: None | str
    task_type: str
    visibility: GetV1PublicJobsJobIdResponse200StagesItemVisibility
    state: (
        GetV1PublicJobsJobIdResponse200StagesItemStateType0
        | GetV1PublicJobsJobIdResponse200StagesItemStateType1
    )
    payout_cents: int | None
    is_unlocked: bool
    public_proof: GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0 | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_stages_item_public_proof_type_0 import (
            GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0,
        )

        stage_id = self.stage_id

        stage_index = self.stage_index

        name: None | str
        name = self.name

        task_type = self.task_type

        visibility = self.visibility.value

        state: str
        if isinstance(self.state, GetV1PublicJobsJobIdResponse200StagesItemStateType0):
            state = self.state.value
        else:
            state = self.state.value

        payout_cents: int | None
        payout_cents = self.payout_cents

        is_unlocked = self.is_unlocked

        public_proof: dict[str, Any] | None | Unset
        if isinstance(self.public_proof, Unset):
            public_proof = UNSET
        elif isinstance(
            self.public_proof, GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0
        ):
            public_proof = self.public_proof.to_dict()
        else:
            public_proof = self.public_proof

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "stageId": stage_id,
                "stageIndex": stage_index,
                "name": name,
                "taskType": task_type,
                "visibility": visibility,
                "state": state,
                "payoutCents": payout_cents,
                "isUnlocked": is_unlocked,
            }
        )
        if public_proof is not UNSET:
            field_dict["publicProof"] = public_proof

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_stages_item_public_proof_type_0 import (
            GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0,
        )

        d = dict(src_dict)
        stage_id = d.pop("stageId")

        stage_index = d.pop("stageIndex")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        task_type = d.pop("taskType")

        visibility = GetV1PublicJobsJobIdResponse200StagesItemVisibility(d.pop("visibility"))

        def _parse_state(
            data: object,
        ) -> (
            GetV1PublicJobsJobIdResponse200StagesItemStateType0
            | GetV1PublicJobsJobIdResponse200StagesItemStateType1
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = GetV1PublicJobsJobIdResponse200StagesItemStateType0(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, str):
                raise TypeError()
            state_type_1 = GetV1PublicJobsJobIdResponse200StagesItemStateType1(data)

            return state_type_1

        state = _parse_state(d.pop("state"))

        def _parse_payout_cents(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_cents = _parse_payout_cents(d.pop("payoutCents"))

        is_unlocked = d.pop("isUnlocked")

        def _parse_public_proof(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                public_proof_type_0 = (
                    GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0.from_dict(data)
                )

                return public_proof_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0 | None | Unset, data
            )

        public_proof = _parse_public_proof(d.pop("publicProof", UNSET))

        get_v1_public_jobs_job_id_response_200_stages_item = cls(
            stage_id=stage_id,
            stage_index=stage_index,
            name=name,
            task_type=task_type,
            visibility=visibility,
            state=state,
            payout_cents=payout_cents,
            is_unlocked=is_unlocked,
            public_proof=public_proof,
        )

        return get_v1_public_jobs_job_id_response_200_stages_item
