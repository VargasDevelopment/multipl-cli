from enum import Enum


class GetV1JobsJobIdResultsResponse402AcceptanceReportType0Status(str, Enum):
    ERROR = "error"
    FAIL = "fail"
    PASS = "pass"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
