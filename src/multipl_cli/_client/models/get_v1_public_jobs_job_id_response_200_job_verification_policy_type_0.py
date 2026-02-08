from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0_rubric_type_0 import (
        GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0")


@_attrs_define
class GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0:
    """
    Attributes:
        required (bool):
        payout_cents (int):
        verifier_task_type (str):
        deadline_seconds (int):
        rubric (GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0 | None | str):
    """

    required: bool
    payout_cents: int
    verifier_task_type: str
    deadline_seconds: int
    rubric: GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0 | None | str

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0_rubric_type_0 import (
            GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0,
        )

        required = self.required

        payout_cents = self.payout_cents

        verifier_task_type = self.verifier_task_type

        deadline_seconds = self.deadline_seconds

        rubric: dict[str, Any] | None | str
        if isinstance(
            self.rubric, GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0
        ):
            rubric = self.rubric.to_dict()
        else:
            rubric = self.rubric

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "required": required,
                "payoutCents": payout_cents,
                "verifierTaskType": verifier_task_type,
                "deadlineSeconds": deadline_seconds,
                "rubric": rubric,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0_rubric_type_0 import (
            GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0,
        )

        d = dict(src_dict)
        required = d.pop("required")

        payout_cents = d.pop("payoutCents")

        verifier_task_type = d.pop("verifierTaskType")

        deadline_seconds = d.pop("deadlineSeconds")

        def _parse_rubric(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0 | None | str:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rubric_type_0 = (
                    GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0.from_dict(
                        data
                    )
                )

                return rubric_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetV1PublicJobsJobIdResponse200JobVerificationPolicyType0RubricType0 | None | str,
                data,
            )

        rubric = _parse_rubric(d.pop("rubric"))

        get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0 = cls(
            required=required,
            payout_cents=payout_cents,
            verifier_task_type=verifier_task_type,
            deadline_seconds=deadline_seconds,
            rubric=rubric,
        )

        return get_v1_public_jobs_job_id_response_200_job_verification_policy_type_0
