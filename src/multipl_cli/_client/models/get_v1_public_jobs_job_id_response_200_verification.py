from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_verification_jobs_item import (
        GetV1PublicJobsJobIdResponse200VerificationJobsItem,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verification_policy_type_0 import (
        GetV1PublicJobsJobIdResponse200VerificationPolicyType0,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200Verification")


@_attrs_define
class GetV1PublicJobsJobIdResponse200Verification:
    """
    Attributes:
        policy (GetV1PublicJobsJobIdResponse200VerificationPolicyType0 | None):
        jobs (list[GetV1PublicJobsJobIdResponse200VerificationJobsItem]):
    """

    policy: GetV1PublicJobsJobIdResponse200VerificationPolicyType0 | None
    jobs: list[GetV1PublicJobsJobIdResponse200VerificationJobsItem]

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_verification_policy_type_0 import (
            GetV1PublicJobsJobIdResponse200VerificationPolicyType0,
        )

        policy: dict[str, Any] | None
        if isinstance(self.policy, GetV1PublicJobsJobIdResponse200VerificationPolicyType0):
            policy = self.policy.to_dict()
        else:
            policy = self.policy

        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "policy": policy,
                "jobs": jobs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_verification_jobs_item import (
            GetV1PublicJobsJobIdResponse200VerificationJobsItem,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verification_policy_type_0 import (
            GetV1PublicJobsJobIdResponse200VerificationPolicyType0,
        )

        d = dict(src_dict)

        def _parse_policy(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200VerificationPolicyType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                policy_type_0 = GetV1PublicJobsJobIdResponse200VerificationPolicyType0.from_dict(
                    data
                )

                return policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetV1PublicJobsJobIdResponse200VerificationPolicyType0 | None, data)

        policy = _parse_policy(d.pop("policy"))

        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = GetV1PublicJobsJobIdResponse200VerificationJobsItem.from_dict(
                jobs_item_data
            )

            jobs.append(jobs_item)

        get_v1_public_jobs_job_id_response_200_verification = cls(
            policy=policy,
            jobs=jobs,
        )

        return get_v1_public_jobs_job_id_response_200_verification
