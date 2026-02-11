from enum import Enum


class GetV1JobsJobIdStagesResponse200StagesItemVisibility(str, Enum):
    GATED = "GATED"
    PUBLIC = "PUBLIC"

    def __str__(self) -> str:
        return str(self.value)
