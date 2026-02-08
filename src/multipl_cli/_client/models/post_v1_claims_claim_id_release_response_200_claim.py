from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.post_v1_claims_claim_id_release_response_200_claim_status import (
    PostV1ClaimsClaimIdReleaseResponse200ClaimStatus,
)

T = TypeVar("T", bound="PostV1ClaimsClaimIdReleaseResponse200Claim")


@_attrs_define
class PostV1ClaimsClaimIdReleaseResponse200Claim:
    """
    Attributes:
        id (str):
        job_id (str):
        worker_id (str):
        status (PostV1ClaimsClaimIdReleaseResponse200ClaimStatus):
        lease_expires_at (str):
        created_at (str):
        released_at (None | str):
        forfeited_at (None | str):
    """

    id: str
    job_id: str
    worker_id: str
    status: PostV1ClaimsClaimIdReleaseResponse200ClaimStatus
    lease_expires_at: str
    created_at: str
    released_at: None | str
    forfeited_at: None | str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        job_id = self.job_id

        worker_id = self.worker_id

        status = self.status.value

        lease_expires_at = self.lease_expires_at

        created_at = self.created_at

        released_at: None | str
        released_at = self.released_at

        forfeited_at: None | str
        forfeited_at = self.forfeited_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "jobId": job_id,
                "workerId": worker_id,
                "status": status,
                "leaseExpiresAt": lease_expires_at,
                "createdAt": created_at,
                "releasedAt": released_at,
                "forfeitedAt": forfeited_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        job_id = d.pop("jobId")

        worker_id = d.pop("workerId")

        status = PostV1ClaimsClaimIdReleaseResponse200ClaimStatus(d.pop("status"))

        lease_expires_at = d.pop("leaseExpiresAt")

        created_at = d.pop("createdAt")

        def _parse_released_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        released_at = _parse_released_at(d.pop("releasedAt"))

        def _parse_forfeited_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        forfeited_at = _parse_forfeited_at(d.pop("forfeitedAt"))

        post_v1_claims_claim_id_release_response_200_claim = cls(
            id=id,
            job_id=job_id,
            worker_id=worker_id,
            status=status,
            lease_expires_at=lease_expires_at,
            created_at=created_at,
            released_at=released_at,
            forfeited_at=forfeited_at,
        )

        return post_v1_claims_claim_id_release_response_200_claim
