from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust_badges_item import (
    GetV1PublicJobsResponse200JobsItemWorkerTrustBadgesItem,
)
from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust_quality_bucket import (
    GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust_sample_size import (
        GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize,
    )


T = TypeVar("T", bound="GetV1PublicJobsResponse200JobsItemWorkerTrust")


@_attrs_define
class GetV1PublicJobsResponse200JobsItemWorkerTrust:
    """
    Attributes:
        sample_size (GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize):
        badges (list[GetV1PublicJobsResponse200JobsItemWorkerTrustBadgesItem]):
        quality_bucket (GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket | Unset):
    """

    sample_size: GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize
    badges: list[GetV1PublicJobsResponse200JobsItemWorkerTrustBadgesItem]
    quality_bucket: GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        sample_size = self.sample_size.to_dict()

        badges = []
        for badges_item_data in self.badges:
            badges_item = badges_item_data.value
            badges.append(badges_item)

        quality_bucket: str | Unset = UNSET
        if not isinstance(self.quality_bucket, Unset):
            quality_bucket = self.quality_bucket.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sampleSize": sample_size,
                "badges": badges,
            }
        )
        if quality_bucket is not UNSET:
            field_dict["qualityBucket"] = quality_bucket

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_response_200_jobs_item_worker_trust_sample_size import (
            GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize,
        )

        d = dict(src_dict)
        sample_size = GetV1PublicJobsResponse200JobsItemWorkerTrustSampleSize.from_dict(
            d.pop("sampleSize")
        )

        badges = []
        _badges = d.pop("badges")
        for badges_item_data in _badges:
            badges_item = GetV1PublicJobsResponse200JobsItemWorkerTrustBadgesItem(badges_item_data)

            badges.append(badges_item)

        _quality_bucket = d.pop("qualityBucket", UNSET)
        quality_bucket: GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket | Unset
        if isinstance(_quality_bucket, Unset):
            quality_bucket = UNSET
        else:
            quality_bucket = GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket(
                _quality_bucket
            )

        get_v1_public_jobs_response_200_jobs_item_worker_trust = cls(
            sample_size=sample_size,
            badges=badges,
            quality_bucket=quality_bucket,
        )

        return get_v1_public_jobs_response_200_jobs_item_worker_trust
