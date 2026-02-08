from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="GetV1MetricsWorkersMeResponse200")


@_attrs_define
class GetV1MetricsWorkersMeResponse200:
    """
    Attributes:
        worker_id (str):
        claims_acquired_all_time (int):
        claims_acquired_last_24_h (int):
        submissions_all_time (int):
        submissions_last_24_h (int):
        paid_jobs_all_time (int):
        paid_jobs_last_24_h (int):
        earned_cents_all_time (int):
        earned_cents_last_24_h (int):
        timestamp (datetime.datetime):
    """

    worker_id: str
    claims_acquired_all_time: int
    claims_acquired_last_24_h: int
    submissions_all_time: int
    submissions_last_24_h: int
    paid_jobs_all_time: int
    paid_jobs_last_24_h: int
    earned_cents_all_time: int
    earned_cents_last_24_h: int
    timestamp: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        worker_id = self.worker_id

        claims_acquired_all_time = self.claims_acquired_all_time

        claims_acquired_last_24_h = self.claims_acquired_last_24_h

        submissions_all_time = self.submissions_all_time

        submissions_last_24_h = self.submissions_last_24_h

        paid_jobs_all_time = self.paid_jobs_all_time

        paid_jobs_last_24_h = self.paid_jobs_last_24_h

        earned_cents_all_time = self.earned_cents_all_time

        earned_cents_last_24_h = self.earned_cents_last_24_h

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "workerId": worker_id,
                "claimsAcquiredAllTime": claims_acquired_all_time,
                "claimsAcquiredLast24h": claims_acquired_last_24_h,
                "submissionsAllTime": submissions_all_time,
                "submissionsLast24h": submissions_last_24_h,
                "paidJobsAllTime": paid_jobs_all_time,
                "paidJobsLast24h": paid_jobs_last_24_h,
                "earnedCentsAllTime": earned_cents_all_time,
                "earnedCentsLast24h": earned_cents_last_24_h,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        worker_id = d.pop("workerId")

        claims_acquired_all_time = d.pop("claimsAcquiredAllTime")

        claims_acquired_last_24_h = d.pop("claimsAcquiredLast24h")

        submissions_all_time = d.pop("submissionsAllTime")

        submissions_last_24_h = d.pop("submissionsLast24h")

        paid_jobs_all_time = d.pop("paidJobsAllTime")

        paid_jobs_last_24_h = d.pop("paidJobsLast24h")

        earned_cents_all_time = d.pop("earnedCentsAllTime")

        earned_cents_last_24_h = d.pop("earnedCentsLast24h")

        timestamp = isoparse(d.pop("timestamp"))

        get_v1_metrics_workers_me_response_200 = cls(
            worker_id=worker_id,
            claims_acquired_all_time=claims_acquired_all_time,
            claims_acquired_last_24_h=claims_acquired_last_24_h,
            submissions_all_time=submissions_all_time,
            submissions_last_24_h=submissions_last_24_h,
            paid_jobs_all_time=paid_jobs_all_time,
            paid_jobs_last_24_h=paid_jobs_last_24_h,
            earned_cents_all_time=earned_cents_all_time,
            earned_cents_last_24_h=earned_cents_last_24_h,
            timestamp=timestamp,
        )

        return get_v1_metrics_workers_me_response_200
