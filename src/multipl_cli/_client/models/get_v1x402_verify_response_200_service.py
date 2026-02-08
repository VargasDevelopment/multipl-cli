from enum import Enum


class GetV1X402VerifyResponse200Service(str, Enum):
    MULTIPL = "multipl"

    def __str__(self) -> str:
        return str(self.value)
