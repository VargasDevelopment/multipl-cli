from enum import Enum


class PostV1JobsJobIdReviewResponse200JobModerationStatusType0(str, Enum):
    FAIL = "fail"
    PASS = "pass"

    def __str__(self) -> str:
        return str(self.value)
