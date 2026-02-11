from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1JobsJobIdStagesResponse200StagesItemProofType0")


@_attrs_define
class GetV1JobsJobIdStagesResponse200StagesItemProofType0:
    """
    Attributes:
        submission_id (None | str):
        artifact_sha_256 (None | str):
        commitment_sha_256 (None | str):
        payee_address (None | str):
    """

    submission_id: None | str
    artifact_sha_256: None | str
    commitment_sha_256: None | str
    payee_address: None | str

    def to_dict(self) -> dict[str, Any]:
        submission_id: None | str
        submission_id = self.submission_id

        artifact_sha_256: None | str
        artifact_sha_256 = self.artifact_sha_256

        commitment_sha_256: None | str
        commitment_sha_256 = self.commitment_sha_256

        payee_address: None | str
        payee_address = self.payee_address

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "submissionId": submission_id,
                "artifactSha256": artifact_sha_256,
                "commitmentSha256": commitment_sha_256,
                "payeeAddress": payee_address,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_submission_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        submission_id = _parse_submission_id(d.pop("submissionId"))

        def _parse_artifact_sha_256(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        artifact_sha_256 = _parse_artifact_sha_256(d.pop("artifactSha256"))

        def _parse_commitment_sha_256(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        commitment_sha_256 = _parse_commitment_sha_256(d.pop("commitmentSha256"))

        def _parse_payee_address(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        payee_address = _parse_payee_address(d.pop("payeeAddress"))

        get_v1_jobs_job_id_stages_response_200_stages_item_proof_type_0 = cls(
            submission_id=submission_id,
            artifact_sha_256=artifact_sha_256,
            commitment_sha_256=commitment_sha_256,
            payee_address=payee_address,
        )

        return get_v1_jobs_job_id_stages_response_200_stages_item_proof_type_0
