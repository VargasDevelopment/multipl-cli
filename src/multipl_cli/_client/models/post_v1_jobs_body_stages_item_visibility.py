from enum import Enum


class PostV1JobsBodyStagesItemVisibility(str, Enum):
    GATED = "GATED"
    PUBLIC = "PUBLIC"

    def __str__(self) -> str:
        return str(self.value)
