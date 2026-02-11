from enum import Enum


class GetV1JobsJobIdStagesResponse200StagesItemAssignmentModeType0(str, Enum):
    OPEN = "open"
    STICKY_FIRST = "sticky_first"

    def __str__(self) -> str:
        return str(self.value)
