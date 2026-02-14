from enum import Enum


class PostV1TrainingSubmitResponse200AcceptanceReportStatus(str, Enum):
    ERROR = "error"
    FAIL = "fail"
    PASS = "pass"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
