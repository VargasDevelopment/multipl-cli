from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200Results")


@_attrs_define
class GetV1PublicJobsJobIdResponse200Results:
    """
    Attributes:
        is_submitted (bool):
        is_unlocked (bool):
        artifact_expires_at (None | str):
    """

    is_submitted: bool
    is_unlocked: bool
    artifact_expires_at: None | str

    def to_dict(self) -> dict[str, Any]:
        is_submitted = self.is_submitted

        is_unlocked = self.is_unlocked

        artifact_expires_at: None | str
        artifact_expires_at = self.artifact_expires_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "isSubmitted": is_submitted,
                "isUnlocked": is_unlocked,
                "artifactExpiresAt": artifact_expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_submitted = d.pop("isSubmitted")

        is_unlocked = d.pop("isUnlocked")

        def _parse_artifact_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        artifact_expires_at = _parse_artifact_expires_at(d.pop("artifactExpiresAt"))

        get_v1_public_jobs_job_id_response_200_results = cls(
            is_submitted=is_submitted,
            is_unlocked=is_unlocked,
            artifact_expires_at=artifact_expires_at,
        )

        return get_v1_public_jobs_job_id_response_200_results
