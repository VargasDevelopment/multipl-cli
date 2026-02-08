from enum import Enum


class GetV1TaskTypesResponse200ItemRole(str, Enum):
    BOTH = "both"
    VERIFIER = "verifier"
    WORKER = "worker"

    def __str__(self) -> str:
        return str(self.value)
