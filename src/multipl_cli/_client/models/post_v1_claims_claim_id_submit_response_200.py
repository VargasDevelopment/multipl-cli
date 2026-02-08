from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_claims_claim_id_submit_response_200_job import (
        PostV1ClaimsClaimIdSubmitResponse200Job,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_submission import (
        PostV1ClaimsClaimIdSubmitResponse200Submission,
    )


T = TypeVar("T", bound="PostV1ClaimsClaimIdSubmitResponse200")


@_attrs_define
class PostV1ClaimsClaimIdSubmitResponse200:
    """
    Attributes:
        submission (PostV1ClaimsClaimIdSubmitResponse200Submission):
        job (PostV1ClaimsClaimIdSubmitResponse200Job):
    """

    submission: PostV1ClaimsClaimIdSubmitResponse200Submission
    job: PostV1ClaimsClaimIdSubmitResponse200Job

    def to_dict(self) -> dict[str, Any]:
        submission = self.submission.to_dict()

        job = self.job.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "submission": submission,
                "job": job,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_claims_claim_id_submit_response_200_job import (
            PostV1ClaimsClaimIdSubmitResponse200Job,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_submission import (
            PostV1ClaimsClaimIdSubmitResponse200Submission,
        )

        d = dict(src_dict)
        submission = PostV1ClaimsClaimIdSubmitResponse200Submission.from_dict(d.pop("submission"))

        job = PostV1ClaimsClaimIdSubmitResponse200Job.from_dict(d.pop("job"))

        post_v1_claims_claim_id_submit_response_200 = cls(
            submission=submission,
            job=job,
        )

        return post_v1_claims_claim_id_submit_response_200
