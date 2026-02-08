from enum import Enum


class PostV1ClaimsClaimIdReleaseResponse200ClaimStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    FORFEITED = "FORFEITED"
    RELEASED = "RELEASED"

    def __str__(self) -> str:
        return str(self.value)
