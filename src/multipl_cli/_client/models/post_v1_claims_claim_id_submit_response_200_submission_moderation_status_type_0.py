from enum import Enum


class PostV1ClaimsClaimIdSubmitResponse200SubmissionModerationStatusType0(str, Enum):
    FAIL = "fail"
    PASS = "pass"

    def __str__(self) -> str:
        return str(self.value)
