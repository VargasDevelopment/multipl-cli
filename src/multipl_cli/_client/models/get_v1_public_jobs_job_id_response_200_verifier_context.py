from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_contract import (
        GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContract,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0 import (
        GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0,
    )
    from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_rubric_type_0 import (
        GetV1PublicJobsJobIdResponse200VerifierContextRubricType0,
    )


T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200VerifierContext")


@_attrs_define
class GetV1PublicJobsJobIdResponse200VerifierContext:
    """
    Attributes:
        parent_job_id (str):
        parent_submission_id (str):
        parent_result_artifact_id (None | str):
        acceptance_report (GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0 | None):
        acceptance_contract (GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContract):
        rubric (GetV1PublicJobsJobIdResponse200VerifierContextRubricType0 | None | str):
        deadline_seconds (int | None):
        preview_json (Any | None | Unset):
    """

    parent_job_id: str
    parent_submission_id: str
    parent_result_artifact_id: None | str
    acceptance_report: GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0 | None
    acceptance_contract: GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContract
    rubric: GetV1PublicJobsJobIdResponse200VerifierContextRubricType0 | None | str
    deadline_seconds: int | None
    preview_json: Any | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0 import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_rubric_type_0 import (
            GetV1PublicJobsJobIdResponse200VerifierContextRubricType0,
        )

        parent_job_id = self.parent_job_id

        parent_submission_id = self.parent_submission_id

        parent_result_artifact_id: None | str
        parent_result_artifact_id = self.parent_result_artifact_id

        acceptance_report: dict[str, Any] | None
        if isinstance(
            self.acceptance_report,
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0,
        ):
            acceptance_report = self.acceptance_report.to_dict()
        else:
            acceptance_report = self.acceptance_report

        acceptance_contract = self.acceptance_contract.to_dict()

        rubric: dict[str, Any] | None | str
        if isinstance(self.rubric, GetV1PublicJobsJobIdResponse200VerifierContextRubricType0):
            rubric = self.rubric.to_dict()
        else:
            rubric = self.rubric

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        preview_json: Any | None | Unset
        if isinstance(self.preview_json, Unset):
            preview_json = UNSET
        else:
            preview_json = self.preview_json

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "parentJobId": parent_job_id,
                "parentSubmissionId": parent_submission_id,
                "parentResultArtifactId": parent_result_artifact_id,
                "acceptanceReport": acceptance_report,
                "acceptanceContract": acceptance_contract,
                "rubric": rubric,
                "deadlineSeconds": deadline_seconds,
            }
        )
        if preview_json is not UNSET:
            field_dict["previewJson"] = preview_json

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_contract import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContract,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_acceptance_report_type_0 import (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0,
        )
        from ..models.get_v1_public_jobs_job_id_response_200_verifier_context_rubric_type_0 import (
            GetV1PublicJobsJobIdResponse200VerifierContextRubricType0,
        )

        d = dict(src_dict)
        parent_job_id = d.pop("parentJobId")

        parent_submission_id = d.pop("parentSubmissionId")

        def _parse_parent_result_artifact_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        parent_result_artifact_id = _parse_parent_result_artifact_id(
            d.pop("parentResultArtifactId")
        )

        def _parse_acceptance_report(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                acceptance_report_type_0 = (
                    GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0.from_dict(
                        data
                    )
                )

                return acceptance_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0 | None, data
            )

        acceptance_report = _parse_acceptance_report(d.pop("acceptanceReport"))

        acceptance_contract = (
            GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceContract.from_dict(
                d.pop("acceptanceContract")
            )
        )

        def _parse_rubric(
            data: object,
        ) -> GetV1PublicJobsJobIdResponse200VerifierContextRubricType0 | None | str:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rubric_type_0 = GetV1PublicJobsJobIdResponse200VerifierContextRubricType0.from_dict(
                    data
                )

                return rubric_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetV1PublicJobsJobIdResponse200VerifierContextRubricType0 | None | str, data
            )

        rubric = _parse_rubric(d.pop("rubric"))

        def _parse_deadline_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        deadline_seconds = _parse_deadline_seconds(d.pop("deadlineSeconds"))

        def _parse_preview_json(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        preview_json = _parse_preview_json(d.pop("previewJson", UNSET))

        get_v1_public_jobs_job_id_response_200_verifier_context = cls(
            parent_job_id=parent_job_id,
            parent_submission_id=parent_submission_id,
            parent_result_artifact_id=parent_result_artifact_id,
            acceptance_report=acceptance_report,
            acceptance_contract=acceptance_contract,
            rubric=rubric,
            deadline_seconds=deadline_seconds,
            preview_json=preview_json,
        )

        return get_v1_public_jobs_job_id_response_200_verifier_context
