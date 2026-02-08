from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_claims_acquire_response_200_claim import (
        PostV1ClaimsAcquireResponse200Claim,
    )
    from ..models.post_v1_claims_acquire_response_200_job import PostV1ClaimsAcquireResponse200Job


T = TypeVar("T", bound="PostV1ClaimsAcquireResponse200")


@_attrs_define
class PostV1ClaimsAcquireResponse200:
    """
    Attributes:
        claim (PostV1ClaimsAcquireResponse200Claim):
        job (PostV1ClaimsAcquireResponse200Job):
    """

    claim: PostV1ClaimsAcquireResponse200Claim
    job: PostV1ClaimsAcquireResponse200Job

    def to_dict(self) -> dict[str, Any]:
        claim = self.claim.to_dict()

        job = self.job.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "claim": claim,
                "job": job,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_claims_acquire_response_200_claim import (
            PostV1ClaimsAcquireResponse200Claim,
        )
        from ..models.post_v1_claims_acquire_response_200_job import (
            PostV1ClaimsAcquireResponse200Job,
        )

        d = dict(src_dict)
        claim = PostV1ClaimsAcquireResponse200Claim.from_dict(d.pop("claim"))

        job = PostV1ClaimsAcquireResponse200Job.from_dict(d.pop("job"))

        post_v1_claims_acquire_response_200 = cls(
            claim=claim,
            job=job,
        )

        return post_v1_claims_acquire_response_200
