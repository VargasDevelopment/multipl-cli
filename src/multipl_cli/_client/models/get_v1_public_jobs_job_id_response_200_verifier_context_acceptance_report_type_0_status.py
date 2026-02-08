from enum import Enum


class GetV1PublicJobsJobIdResponse200VerifierContextAcceptanceReportType0Status(str, Enum):
    ERROR = "error"
    FAIL = "fail"
    PASS = "pass"
    SKIPPED = "skipped"

    def __str__(self) -> str:
        return str(self.value)
