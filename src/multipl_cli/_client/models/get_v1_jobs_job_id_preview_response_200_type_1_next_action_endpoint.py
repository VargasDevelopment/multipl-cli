from enum import Enum


class GetV1JobsJobIdPreviewResponse200Type1NextActionEndpoint(str, Enum):
    VALUE_0 = "/v1/jobs/:jobId/results"

    def __str__(self) -> str:
        return str(self.value)
