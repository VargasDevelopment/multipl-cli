from enum import Enum


class GetV1X402VerifyResponse200Kind(str, Enum):
    X402_VERIFY = "x402_verify"

    def __str__(self) -> str:
        return str(self.value)
