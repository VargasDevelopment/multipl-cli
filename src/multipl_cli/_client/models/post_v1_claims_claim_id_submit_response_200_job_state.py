from enum import Enum


class PostV1ClaimsClaimIdSubmitResponse200JobState(str, Enum):
    ACCEPTED = "ACCEPTED"
    AVAILABLE = "AVAILABLE"
    CANCELLED = "CANCELLED"
    CLAIMED = "CLAIMED"
    DRAFT = "DRAFT"
    EXPIRED = "EXPIRED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"
    SUBMITTED = "SUBMITTED"

    def __str__(self) -> str:
        return str(self.value)
