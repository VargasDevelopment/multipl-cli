from enum import Enum


class GetV1JobsJobIdResponse200JobModerationStatusType0(str, Enum):
    FAIL = "fail"
    PASS = "pass"

    def __str__(self) -> str:
        return str(self.value)
