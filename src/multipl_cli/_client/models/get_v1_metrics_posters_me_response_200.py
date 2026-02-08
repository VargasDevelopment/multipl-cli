from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="GetV1MetricsPostersMeResponse200")


@_attrs_define
class GetV1MetricsPostersMeResponse200:
    """
    Attributes:
        poster_id (str):
        jobs_posted_all_time (int):
        jobs_posted_last_24_h (int):
        jobs_unlocked_all_time (int):
        jobs_unlocked_last_24_h (int):
        unlocked_cents_all_time (int):
        unlocked_cents_last_24_h (int):
        submitted_unpaid_now (int):
        timestamp (datetime.datetime):
    """

    poster_id: str
    jobs_posted_all_time: int
    jobs_posted_last_24_h: int
    jobs_unlocked_all_time: int
    jobs_unlocked_last_24_h: int
    unlocked_cents_all_time: int
    unlocked_cents_last_24_h: int
    submitted_unpaid_now: int
    timestamp: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        poster_id = self.poster_id

        jobs_posted_all_time = self.jobs_posted_all_time

        jobs_posted_last_24_h = self.jobs_posted_last_24_h

        jobs_unlocked_all_time = self.jobs_unlocked_all_time

        jobs_unlocked_last_24_h = self.jobs_unlocked_last_24_h

        unlocked_cents_all_time = self.unlocked_cents_all_time

        unlocked_cents_last_24_h = self.unlocked_cents_last_24_h

        submitted_unpaid_now = self.submitted_unpaid_now

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "posterId": poster_id,
                "jobsPostedAllTime": jobs_posted_all_time,
                "jobsPostedLast24h": jobs_posted_last_24_h,
                "jobsUnlockedAllTime": jobs_unlocked_all_time,
                "jobsUnlockedLast24h": jobs_unlocked_last_24_h,
                "unlockedCentsAllTime": unlocked_cents_all_time,
                "unlockedCentsLast24h": unlocked_cents_last_24_h,
                "submittedUnpaidNow": submitted_unpaid_now,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        poster_id = d.pop("posterId")

        jobs_posted_all_time = d.pop("jobsPostedAllTime")

        jobs_posted_last_24_h = d.pop("jobsPostedLast24h")

        jobs_unlocked_all_time = d.pop("jobsUnlockedAllTime")

        jobs_unlocked_last_24_h = d.pop("jobsUnlockedLast24h")

        unlocked_cents_all_time = d.pop("unlockedCentsAllTime")

        unlocked_cents_last_24_h = d.pop("unlockedCentsLast24h")

        submitted_unpaid_now = d.pop("submittedUnpaidNow")

        timestamp = isoparse(d.pop("timestamp"))

        get_v1_metrics_posters_me_response_200 = cls(
            poster_id=poster_id,
            jobs_posted_all_time=jobs_posted_all_time,
            jobs_posted_last_24_h=jobs_posted_last_24_h,
            jobs_unlocked_all_time=jobs_unlocked_all_time,
            jobs_unlocked_last_24_h=jobs_unlocked_last_24_h,
            unlocked_cents_all_time=unlocked_cents_all_time,
            unlocked_cents_last_24_h=unlocked_cents_last_24_h,
            submitted_unpaid_now=submitted_unpaid_now,
            timestamp=timestamp,
        )

        return get_v1_metrics_posters_me_response_200
