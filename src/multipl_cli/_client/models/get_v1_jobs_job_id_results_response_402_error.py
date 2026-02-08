from enum import Enum


class GetV1JobsJobIdResultsResponse402Error(str, Enum):
    PAYMENT_REQUIRED = "payment_required"

    def __str__(self) -> str:
        return str(self.value)
