from enum import Enum


class GetV1PublicJobsResponse200JobsItemWorkerTrustBadgesItem(str, Enum):
    HIGH_QUALITY = "high_quality"
    RELIABLE_DELIVERY = "reliable_delivery"

    def __str__(self) -> str:
        return str(self.value)
