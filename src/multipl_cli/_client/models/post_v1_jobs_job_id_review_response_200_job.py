from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_status_type_0 import (
    PostV1JobsJobIdReviewResponse200JobModerationStatusType0,
)
from ..models.post_v1_jobs_job_id_review_response_200_job_state import (
    PostV1JobsJobIdReviewResponse200JobState,
)

if TYPE_CHECKING:
    from ..models.post_v1_jobs_job_id_review_response_200_job_acceptance import (
        PostV1JobsJobIdReviewResponse200JobAcceptance,
    )
    from ..models.post_v1_jobs_job_id_review_response_200_job_input import (
        PostV1JobsJobIdReviewResponse200JobInput,
    )
    from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_categories_type_0 import (
        PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0,
    )
    from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_scores_type_0 import (
        PostV1JobsJobIdReviewResponse200JobModerationScoresType0,
    )


T = TypeVar("T", bound="PostV1JobsJobIdReviewResponse200Job")


@_attrs_define
class PostV1JobsJobIdReviewResponse200Job:
    """
    Attributes:
        id (str):
        poster_id (str):
        task_type (str):
        input_ (PostV1JobsJobIdReviewResponse200JobInput):
        acceptance (PostV1JobsJobIdReviewResponse200JobAcceptance):
        requested_model (None | str):
        estimated_tokens (int | None):
        deadline_seconds (int | None):
        payout_cents (int | None):
        state (PostV1JobsJobIdReviewResponse200JobState):
        created_at (str):
        updated_at (str):
        available_at (None | str):
        claimed_at (None | str):
        completed_at (None | str):
        expires_at (str):
        moderation_status (None | PostV1JobsJobIdReviewResponse200JobModerationStatusType0):
        moderation_model (None | str):
        moderation_categories (None | PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0):
        moderation_scores (None | PostV1JobsJobIdReviewResponse200JobModerationScoresType0):
        moderation_at (None | str):
        content_sha_256 (None | str):
    """

    id: str
    poster_id: str
    task_type: str
    input_: PostV1JobsJobIdReviewResponse200JobInput
    acceptance: PostV1JobsJobIdReviewResponse200JobAcceptance
    requested_model: None | str
    estimated_tokens: int | None
    deadline_seconds: int | None
    payout_cents: int | None
    state: PostV1JobsJobIdReviewResponse200JobState
    created_at: str
    updated_at: str
    available_at: None | str
    claimed_at: None | str
    completed_at: None | str
    expires_at: str
    moderation_status: None | PostV1JobsJobIdReviewResponse200JobModerationStatusType0
    moderation_model: None | str
    moderation_categories: None | PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0
    moderation_scores: None | PostV1JobsJobIdReviewResponse200JobModerationScoresType0
    moderation_at: None | str
    content_sha_256: None | str

    def to_dict(self) -> dict[str, Any]:
        from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_categories_type_0 import (
            PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0,
        )
        from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_scores_type_0 import (
            PostV1JobsJobIdReviewResponse200JobModerationScoresType0,
        )

        id = self.id

        poster_id = self.poster_id

        task_type = self.task_type

        input_ = self.input_.to_dict()

        acceptance = self.acceptance.to_dict()

        requested_model: None | str
        requested_model = self.requested_model

        estimated_tokens: int | None
        estimated_tokens = self.estimated_tokens

        deadline_seconds: int | None
        deadline_seconds = self.deadline_seconds

        payout_cents: int | None
        payout_cents = self.payout_cents

        state = self.state.value

        created_at = self.created_at

        updated_at = self.updated_at

        available_at: None | str
        available_at = self.available_at

        claimed_at: None | str
        claimed_at = self.claimed_at

        completed_at: None | str
        completed_at = self.completed_at

        expires_at = self.expires_at

        moderation_status: None | str
        if isinstance(
            self.moderation_status, PostV1JobsJobIdReviewResponse200JobModerationStatusType0
        ):
            moderation_status = self.moderation_status.value
        else:
            moderation_status = self.moderation_status

        moderation_model: None | str
        moderation_model = self.moderation_model

        moderation_categories: dict[str, Any] | None
        if isinstance(
            self.moderation_categories, PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0
        ):
            moderation_categories = self.moderation_categories.to_dict()
        else:
            moderation_categories = self.moderation_categories

        moderation_scores: dict[str, Any] | None
        if isinstance(
            self.moderation_scores, PostV1JobsJobIdReviewResponse200JobModerationScoresType0
        ):
            moderation_scores = self.moderation_scores.to_dict()
        else:
            moderation_scores = self.moderation_scores

        moderation_at: None | str
        moderation_at = self.moderation_at

        content_sha_256: None | str
        content_sha_256 = self.content_sha_256

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "posterId": poster_id,
                "taskType": task_type,
                "input": input_,
                "acceptance": acceptance,
                "requestedModel": requested_model,
                "estimatedTokens": estimated_tokens,
                "deadlineSeconds": deadline_seconds,
                "payoutCents": payout_cents,
                "state": state,
                "createdAt": created_at,
                "updatedAt": updated_at,
                "availableAt": available_at,
                "claimedAt": claimed_at,
                "completedAt": completed_at,
                "expiresAt": expires_at,
                "moderationStatus": moderation_status,
                "moderationModel": moderation_model,
                "moderationCategories": moderation_categories,
                "moderationScores": moderation_scores,
                "moderationAt": moderation_at,
                "contentSha256": content_sha_256,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_jobs_job_id_review_response_200_job_acceptance import (
            PostV1JobsJobIdReviewResponse200JobAcceptance,
        )
        from ..models.post_v1_jobs_job_id_review_response_200_job_input import (
            PostV1JobsJobIdReviewResponse200JobInput,
        )
        from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_categories_type_0 import (
            PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0,
        )
        from ..models.post_v1_jobs_job_id_review_response_200_job_moderation_scores_type_0 import (
            PostV1JobsJobIdReviewResponse200JobModerationScoresType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        poster_id = d.pop("posterId")

        task_type = d.pop("taskType")

        input_ = PostV1JobsJobIdReviewResponse200JobInput.from_dict(d.pop("input"))

        acceptance = PostV1JobsJobIdReviewResponse200JobAcceptance.from_dict(d.pop("acceptance"))

        def _parse_requested_model(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        requested_model = _parse_requested_model(d.pop("requestedModel"))

        def _parse_estimated_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        estimated_tokens = _parse_estimated_tokens(d.pop("estimatedTokens"))

        def _parse_deadline_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        deadline_seconds = _parse_deadline_seconds(d.pop("deadlineSeconds"))

        def _parse_payout_cents(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_cents = _parse_payout_cents(d.pop("payoutCents"))

        state = PostV1JobsJobIdReviewResponse200JobState(d.pop("state"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        def _parse_available_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        available_at = _parse_available_at(d.pop("availableAt"))

        def _parse_claimed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        claimed_at = _parse_claimed_at(d.pop("claimedAt"))

        def _parse_completed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        completed_at = _parse_completed_at(d.pop("completedAt"))

        expires_at = d.pop("expiresAt")

        def _parse_moderation_status(
            data: object,
        ) -> None | PostV1JobsJobIdReviewResponse200JobModerationStatusType0:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                moderation_status_type_0 = PostV1JobsJobIdReviewResponse200JobModerationStatusType0(
                    data
                )

                return moderation_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PostV1JobsJobIdReviewResponse200JobModerationStatusType0, data)

        moderation_status = _parse_moderation_status(d.pop("moderationStatus"))

        def _parse_moderation_model(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        moderation_model = _parse_moderation_model(d.pop("moderationModel"))

        def _parse_moderation_categories(
            data: object,
        ) -> None | PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                moderation_categories_type_0 = (
                    PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0.from_dict(data)
                )

                return moderation_categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PostV1JobsJobIdReviewResponse200JobModerationCategoriesType0, data)

        moderation_categories = _parse_moderation_categories(d.pop("moderationCategories"))

        def _parse_moderation_scores(
            data: object,
        ) -> None | PostV1JobsJobIdReviewResponse200JobModerationScoresType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                moderation_scores_type_0 = (
                    PostV1JobsJobIdReviewResponse200JobModerationScoresType0.from_dict(data)
                )

                return moderation_scores_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PostV1JobsJobIdReviewResponse200JobModerationScoresType0, data)

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

        post_v1_jobs_job_id_review_response_200_job = cls(
            id=id,
            poster_id=poster_id,
            task_type=task_type,
            input_=input_,
            acceptance=acceptance,
            requested_model=requested_model,
            estimated_tokens=estimated_tokens,
            deadline_seconds=deadline_seconds,
            payout_cents=payout_cents,
            state=state,
            created_at=created_at,
            updated_at=updated_at,
            available_at=available_at,
            claimed_at=claimed_at,
            completed_at=completed_at,
            expires_at=expires_at,
            moderation_status=moderation_status,
            moderation_model=moderation_model,
            moderation_categories=moderation_categories,
            moderation_scores=moderation_scores,
            moderation_at=moderation_at,
            content_sha_256=content_sha_256,
        )

        return post_v1_jobs_job_id_review_response_200_job
