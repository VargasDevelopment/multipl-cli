from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetV1PublicStatsResponse200")


@_attrs_define
class GetV1PublicStatsResponse200:
    """
    Attributes:
        jobs_created_all_time (int):
        jobs_completed_all_time (int):
        jobs_active_now (int):
        jobs_completed_last_24_h (int):
        workers_seen_last_24_h (int):
        unlocked_cents_last_24_h (int):
        available_jobs_now (int | Unset):
        active_claims_now (int | Unset):
    """

    jobs_created_all_time: int
    jobs_completed_all_time: int
    jobs_active_now: int
    jobs_completed_last_24_h: int
    workers_seen_last_24_h: int
    unlocked_cents_last_24_h: int
    available_jobs_now: int | Unset = UNSET
    active_claims_now: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        jobs_created_all_time = self.jobs_created_all_time

        jobs_completed_all_time = self.jobs_completed_all_time

        jobs_active_now = self.jobs_active_now

        jobs_completed_last_24_h = self.jobs_completed_last_24_h

        workers_seen_last_24_h = self.workers_seen_last_24_h

        unlocked_cents_last_24_h = self.unlocked_cents_last_24_h

        available_jobs_now = self.available_jobs_now

        active_claims_now = self.active_claims_now

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobsCreatedAllTime": jobs_created_all_time,
                "jobsCompletedAllTime": jobs_completed_all_time,
                "jobsActiveNow": jobs_active_now,
                "jobsCompletedLast24h": jobs_completed_last_24_h,
                "workersSeenLast24h": workers_seen_last_24_h,
                "unlockedCentsLast24h": unlocked_cents_last_24_h,
            }
        )
        if available_jobs_now is not UNSET:
            field_dict["availableJobsNow"] = available_jobs_now
        if active_claims_now is not UNSET:
            field_dict["activeClaimsNow"] = active_claims_now

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        jobs_created_all_time = d.pop("jobsCreatedAllTime")

        jobs_completed_all_time = d.pop("jobsCompletedAllTime")

        jobs_active_now = d.pop("jobsActiveNow")

        jobs_completed_last_24_h = d.pop("jobsCompletedLast24h")

        workers_seen_last_24_h = d.pop("workersSeenLast24h")

        unlocked_cents_last_24_h = d.pop("unlockedCentsLast24h")

        available_jobs_now = d.pop("availableJobsNow", UNSET)

        active_claims_now = d.pop("activeClaimsNow", UNSET)

        get_v1_public_stats_response_200 = cls(
            jobs_created_all_time=jobs_created_all_time,
            jobs_completed_all_time=jobs_completed_all_time,
            jobs_active_now=jobs_active_now,
            jobs_completed_last_24_h=jobs_completed_last_24_h,
            workers_seen_last_24_h=workers_seen_last_24_h,
            unlocked_cents_last_24_h=unlocked_cents_last_24_h,
            available_jobs_now=available_jobs_now,
            active_claims_now=active_claims_now,
        )

        return get_v1_public_stats_response_200
