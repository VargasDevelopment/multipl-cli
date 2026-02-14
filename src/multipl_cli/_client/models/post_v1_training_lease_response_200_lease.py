from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="PostV1TrainingLeaseResponse200Lease")


@_attrs_define
class PostV1TrainingLeaseResponse200Lease:
    """
    Attributes:
        lease_id (str):
        submit_token (str):
        exercise_id (str):
        task_type (str):
        issued_at (datetime.datetime):
        expires_at (datetime.datetime):
        ttl_seconds (int):
    """

    lease_id: str
    submit_token: str
    exercise_id: str
    task_type: str
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    ttl_seconds: int

    def to_dict(self) -> dict[str, Any]:
        lease_id = self.lease_id

        submit_token = self.submit_token

        exercise_id = self.exercise_id

        task_type = self.task_type

        issued_at = self.issued_at.isoformat()

        expires_at = self.expires_at.isoformat()

        ttl_seconds = self.ttl_seconds

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "leaseId": lease_id,
                "submitToken": submit_token,
                "exerciseId": exercise_id,
                "taskType": task_type,
                "issuedAt": issued_at,
                "expiresAt": expires_at,
                "ttlSeconds": ttl_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lease_id = d.pop("leaseId")

        submit_token = d.pop("submitToken")

        exercise_id = d.pop("exerciseId")

        task_type = d.pop("taskType")

        issued_at = isoparse(d.pop("issuedAt"))

        expires_at = isoparse(d.pop("expiresAt"))

        ttl_seconds = d.pop("ttlSeconds")

        post_v1_training_lease_response_200_lease = cls(
            lease_id=lease_id,
            submit_token=submit_token,
            exercise_id=exercise_id,
            task_type=task_type,
            issued_at=issued_at,
            expires_at=expires_at,
            ttl_seconds=ttl_seconds,
        )

        return post_v1_training_lease_response_200_lease
