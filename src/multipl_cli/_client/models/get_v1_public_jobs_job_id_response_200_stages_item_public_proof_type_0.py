from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0")


@_attrs_define
class GetV1PublicJobsJobIdResponse200StagesItemPublicProofType0:
    """
    Attributes:
        job_id (str):
        stage_id (str):
        stage_index (int):
        submission_id (None | str):
        artifact_sha_256 (None | str):
        commitment_sha_256 (None | str):
        receipt_id (str):
        paid_at (str):
        payee_address (str):
    """

    job_id: str
    stage_id: str
    stage_index: int
    submission_id: None | str
    artifact_sha_256: None | str
    commitment_sha_256: None | str
    receipt_id: str
    paid_at: str
    payee_address: str

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        stage_id = self.stage_id

        stage_index = self.stage_index

        submission_id: None | str
        submission_id = self.submission_id

        artifact_sha_256: None | str
        artifact_sha_256 = self.artifact_sha_256

        commitment_sha_256: None | str
        commitment_sha_256 = self.commitment_sha_256

        receipt_id = self.receipt_id

        paid_at = self.paid_at

        payee_address = self.payee_address

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "jobId": job_id,
                "stageId": stage_id,
                "stageIndex": stage_index,
                "submissionId": submission_id,
                "artifactSha256": artifact_sha_256,
                "commitmentSha256": commitment_sha_256,
                "receiptId": receipt_id,
                "paidAt": paid_at,
                "payeeAddress": payee_address,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("jobId")

        stage_id = d.pop("stageId")

        stage_index = d.pop("stageIndex")

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

        receipt_id = d.pop("receiptId")

        paid_at = d.pop("paidAt")

        payee_address = d.pop("payeeAddress")

        get_v1_public_jobs_job_id_response_200_stages_item_public_proof_type_0 = cls(
            job_id=job_id,
            stage_id=stage_id,
            stage_index=stage_index,
            submission_id=submission_id,
            artifact_sha_256=artifact_sha_256,
            commitment_sha_256=commitment_sha_256,
            receipt_id=receipt_id,
            paid_at=paid_at,
            payee_address=payee_address,
        )

        return get_v1_public_jobs_job_id_response_200_stages_item_public_proof_type_0
