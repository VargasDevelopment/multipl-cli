from enum import Enum


class GetV1X402VerifyResponse402Error(str, Enum):
    PAYMENT_REQUIRED = "payment_required"

    def __str__(self) -> str:
        return str(self.value)
