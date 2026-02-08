from enum import Enum


class GetV1JobsJobIdPreviewResponse200Type0Reason(str, Enum):
    SAFETY_CHECKS = "safety_checks"

    def __str__(self) -> str:
        return str(self.value)
