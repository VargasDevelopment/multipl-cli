from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_v1_jobs_job_id_results_response_200_result import (
        GetV1JobsJobIdResultsResponse200Result,
    )


T = TypeVar("T", bound="GetV1JobsJobIdResultsResponse200")


@_attrs_define
class GetV1JobsJobIdResultsResponse200:
    """
    Attributes:
        result (GetV1JobsJobIdResultsResponse200Result):
    """

    result: GetV1JobsJobIdResultsResponse200Result

    def to_dict(self) -> dict[str, Any]:
        result = self.result.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_jobs_job_id_results_response_200_result import (
            GetV1JobsJobIdResultsResponse200Result,
        )

        d = dict(src_dict)
        result = GetV1JobsJobIdResultsResponse200Result.from_dict(d.pop("result"))

        get_v1_jobs_job_id_results_response_200 = cls(
            result=result,
        )

        return get_v1_jobs_job_id_results_response_200
