from enum import Enum


class GetV1PublicJobsResponse200JobsItemPosterTrustBadgesItem(str, Enum):
    FAST_PAYER = "fast_payer"
    RELIABLE_UNLOCKER = "reliable_unlocker"

    def __str__(self) -> str:
        return str(self.value)
