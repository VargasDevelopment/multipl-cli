from enum import Enum


class GetV1JobsLane(str, Enum):
    VERIFIER = "verifier"

    def __str__(self) -> str:
        return str(self.value)
