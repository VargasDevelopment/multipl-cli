from enum import Enum


class PostV1TrainingValidateJobBodyStagesItemAssignmentMode(str, Enum):
    OPEN = "open"
    STICKY_FIRST = "sticky_first"

    def __str__(self) -> str:
        return str(self.value)
