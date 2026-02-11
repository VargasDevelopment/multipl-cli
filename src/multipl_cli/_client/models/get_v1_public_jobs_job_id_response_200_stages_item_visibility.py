from enum import Enum


class GetV1PublicJobsJobIdResponse200StagesItemVisibility(str, Enum):
    GATED = "GATED"
    PUBLIC = "PUBLIC"

    def __str__(self) -> str:
        return str(self.value)
