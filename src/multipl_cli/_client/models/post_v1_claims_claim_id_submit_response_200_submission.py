from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_status_type_0 import (
    PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0,
)
from ..models.post_v1_claims_claim_id_submit_response_200_submission_quarantine_reason_type_0 import (
    PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_categories_type_0 import (
        PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0,
    )
    from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_scores_type_0 import (
        PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0,
    )


T = TypeVar("T", bound="PostV1ClaimsClaimIdSubmitResponse200Submission")


@_attrs_define
class PostV1ClaimsClaimIdSubmitResponse200Submission:
    """
    Attributes:
        id (str):
        job_id (str):
        claim_id (None | str):
        worker_id (str):
        moderation_status (None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0):
        moderation_model (None | str):
        moderation_categories (None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0):
        moderation_scores (None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0):
        moderation_at (None | str):
        content_sha_256 (None | str):
        quarantine_reason (None | PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0):
        model_used (None | str):
        tokens_used (int | None):
        created_at (str):
        output (Any | Unset):
    """

    id: str
    job_id: str
    claim_id: None | str
    worker_id: str
    moderation_status: None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0
    moderation_model: None | str
    moderation_categories: (
        None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0
    )
    moderation_scores: None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0
    moderation_at: None | str
    content_sha_256: None | str
    quarantine_reason: None | PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0
    model_used: None | str
    tokens_used: int | None
    created_at: str
    output: Any | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_categories_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_scores_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0,
        )

        id = self.id

        job_id = self.job_id

        claim_id: None | str
        claim_id = self.claim_id

        worker_id = self.worker_id

        moderation_status: None | str
        if isinstance(
            self.moderation_status,
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0,
        ):
            moderation_status = self.moderation_status.value
        else:
            moderation_status = self.moderation_status

        moderation_model: None | str
        moderation_model = self.moderation_model

        moderation_categories: dict[str, Any] | None
        if isinstance(
            self.moderation_categories,
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0,
        ):
            moderation_categories = self.moderation_categories.to_dict()
        else:
            moderation_categories = self.moderation_categories

        moderation_scores: dict[str, Any] | None
        if isinstance(
            self.moderation_scores,
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0,
        ):
            moderation_scores = self.moderation_scores.to_dict()
        else:
            moderation_scores = self.moderation_scores

        moderation_at: None | str
        moderation_at = self.moderation_at

        content_sha_256: None | str
        content_sha_256 = self.content_sha_256

        quarantine_reason: None | str
        if isinstance(
            self.quarantine_reason,
            PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0,
        ):
            quarantine_reason = self.quarantine_reason.value
        else:
            quarantine_reason = self.quarantine_reason

        model_used: None | str
        model_used = self.model_used

        tokens_used: int | None
        tokens_used = self.tokens_used

        created_at = self.created_at

        output = self.output

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "jobId": job_id,
                "claimId": claim_id,
                "workerId": worker_id,
                "moderationStatus": moderation_status,
                "moderationModel": moderation_model,
                "moderationCategories": moderation_categories,
                "moderationScores": moderation_scores,
                "moderationAt": moderation_at,
                "contentSha256": content_sha_256,
                "quarantineReason": quarantine_reason,
                "modelUsed": model_used,
                "tokensUsed": tokens_used,
                "createdAt": created_at,
            }
        )
        if output is not UNSET:
            field_dict["output"] = output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_categories_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0,
        )
        from ..models.post_v1_claims_claim_id_submit_response_200_submission_moderation_scores_type_0 import (
            PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        job_id = d.pop("jobId")

        def _parse_claim_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        claim_id = _parse_claim_id(d.pop("claimId"))

        worker_id = d.pop("workerId")

        def _parse_moderation_status(
            data: object,
        ) -> None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                moderation_status_type_0 = (
                    PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0(data)
                )

                return moderation_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0, data
            )

        moderation_status = _parse_moderation_status(d.pop("moderationStatus"))

        def _parse_moderation_model(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        moderation_model = _parse_moderation_model(d.pop("moderationModel"))

        def _parse_moderation_categories(
            data: object,
        ) -> None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                moderation_categories_type_0 = PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0.from_dict(
                    data
                )

                return moderation_categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationCategoriesType0, data
            )

        moderation_categories = _parse_moderation_categories(d.pop("moderationCategories"))

        def _parse_moderation_scores(
            data: object,
        ) -> None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                moderation_scores_type_0 = (
                    PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0.from_dict(
                        data
                    )
                )

                return moderation_scores_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationScoresType0, data
            )

        moderation_scores = _parse_moderation_scores(d.pop("moderationScores"))

        def _parse_moderation_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        moderation_at = _parse_moderation_at(d.pop("moderationAt"))

        def _parse_content_sha_256(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        content_sha_256 = _parse_content_sha_256(d.pop("contentSha256"))

        def _parse_quarantine_reason(
            data: object,
        ) -> None | PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                quarantine_reason_type_0 = (
                    PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0(data)
                )

                return quarantine_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PostV1ClaimsClaimIdSubmitResponse200SubmissionQuarantineReasonType0, data
            )

        quarantine_reason = _parse_quarantine_reason(d.pop("quarantineReason"))

        def _parse_model_used(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        model_used = _parse_model_used(d.pop("modelUsed"))

        def _parse_tokens_used(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        tokens_used = _parse_tokens_used(d.pop("tokensUsed"))

        created_at = d.pop("createdAt")

        output = d.pop("output", UNSET)

        post_v1_claims_claim_id_submit_response_200_submission = cls(
            id=id,
            job_id=job_id,
            claim_id=claim_id,
            worker_id=worker_id,
            moderation_status=moderation_status,
            moderation_model=moderation_model,
            moderation_categories=moderation_categories,
            moderation_scores=moderation_scores,
            moderation_at=moderation_at,
            content_sha_256=content_sha_256,
            quarantine_reason=quarantine_reason,
            model_used=model_used,
            tokens_used=tokens_used,
            created_at=created_at,
            output=output,
        )

        return post_v1_claims_claim_id_submit_response_200_submission
