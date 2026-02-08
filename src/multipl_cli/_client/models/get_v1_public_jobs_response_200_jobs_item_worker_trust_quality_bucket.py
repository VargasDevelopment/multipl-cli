from enum import Enum


class GetV1PublicJobsResponse200JobsItemWorkerTrustQualityBucket(str, Enum):
    ELITE = "elite"
    HIGH = "high"
    LOW = "low"
    MEDIUM = "medium"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
