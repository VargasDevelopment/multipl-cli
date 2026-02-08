from enum import Enum


class GetV1JobsJobIdPreviewResponse200Type1NextActionKind(str, Enum):
    X402_UNLOCK_RESULTS = "x402_unlock_results"

    def __str__(self) -> str:
        return str(self.value)
