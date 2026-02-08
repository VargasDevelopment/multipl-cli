from enum import Enum


class GetV1WorkersStatusResponse200Status(str, Enum):
    CLAIMED = "claimed"
    PENDING_CLAIM = "pending_claim"

    def __str__(self) -> str:
        return str(self.value)
