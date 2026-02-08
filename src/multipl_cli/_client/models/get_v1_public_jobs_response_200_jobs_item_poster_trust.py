from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust_badges_item import (
    GetV1PublicJobsResponse200JobsItemPosterTrustBadgesItem,
)
from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust_unlock_rate_bucket import (
    GetV1PublicJobsResponse200JobsItemPosterTrustUnlockRateBucket,
)

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust_sample_size import (
        GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize,
    )


T = TypeVar("T", bound="GetV1PublicJobsResponse200JobsItemPosterTrust")


@_attrs_define
class GetV1PublicJobsResponse200JobsItemPosterTrust:
    """
    Attributes:
        sample_size (GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize):
        unlock_rate_bucket (GetV1PublicJobsResponse200JobsItemPosterTrustUnlockRateBucket):
        badges (list[GetV1PublicJobsResponse200JobsItemPosterTrustBadgesItem]):
    """

    sample_size: GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize
    unlock_rate_bucket: GetV1PublicJobsResponse200JobsItemPosterTrustUnlockRateBucket
    badges: list[GetV1PublicJobsResponse200JobsItemPosterTrustBadgesItem]

    def to_dict(self) -> dict[str, Any]:
        sample_size = self.sample_size.to_dict()

        unlock_rate_bucket = self.unlock_rate_bucket.value

        badges = []
        for badges_item_data in self.badges:
            badges_item = badges_item_data.value
            badges.append(badges_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sampleSize": sample_size,
                "unlockRateBucket": unlock_rate_bucket,
                "badges": badges,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_response_200_jobs_item_poster_trust_sample_size import (
            GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize,
        )

        d = dict(src_dict)
        sample_size = GetV1PublicJobsResponse200JobsItemPosterTrustSampleSize.from_dict(
            d.pop("sampleSize")
        )

        unlock_rate_bucket = GetV1PublicJobsResponse200JobsItemPosterTrustUnlockRateBucket(
            d.pop("unlockRateBucket")
        )

        badges = []
        _badges = d.pop("badges")
        for badges_item_data in _badges:
            badges_item = GetV1PublicJobsResponse200JobsItemPosterTrustBadgesItem(badges_item_data)

            badges.append(badges_item)

        get_v1_public_jobs_response_200_jobs_item_poster_trust = cls(
            sample_size=sample_size,
            unlock_rate_bucket=unlock_rate_bucket,
            badges=badges,
        )

        return get_v1_public_jobs_response_200_jobs_item_poster_trust
