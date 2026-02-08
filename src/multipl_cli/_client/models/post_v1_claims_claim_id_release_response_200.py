from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_claims_claim_id_release_response_200_claim import (
        PostV1ClaimsClaimIdReleaseResponse200Claim,
    )
    from ..models.post_v1_claims_claim_id_release_response_200_job import (
        PostV1ClaimsClaimIdReleaseResponse200Job,
    )


T = TypeVar("T", bound="PostV1ClaimsClaimIdReleaseResponse200")


@_attrs_define
class PostV1ClaimsClaimIdReleaseResponse200:
    """
    Attributes:
        ok (bool):
        job (PostV1ClaimsClaimIdReleaseResponse200Job):
        claim (PostV1ClaimsClaimIdReleaseResponse200Claim):
    """

    ok: bool
    job: PostV1ClaimsClaimIdReleaseResponse200Job
    claim: PostV1ClaimsClaimIdReleaseResponse200Claim

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        job = self.job.to_dict()

        claim = self.claim.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "job": job,
                "claim": claim,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_claims_claim_id_release_response_200_claim import (
            PostV1ClaimsClaimIdReleaseResponse200Claim,
        )
        from ..models.post_v1_claims_claim_id_release_response_200_job import (
            PostV1ClaimsClaimIdReleaseResponse200Job,
        )

        d = dict(src_dict)
        ok = d.pop("ok")

        job = PostV1ClaimsClaimIdReleaseResponse200Job.from_dict(d.pop("job"))

        claim = PostV1ClaimsClaimIdReleaseResponse200Claim.from_dict(d.pop("claim"))

        post_v1_claims_claim_id_release_response_200 = cls(
            ok=ok,
            job=job,
            claim=claim,
        )

        return post_v1_claims_claim_id_release_response_200
