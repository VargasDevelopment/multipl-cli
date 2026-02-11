from enum import Enum


class GetV1PublicJobsJobIdResponse200StagesItemStateType1(str, Enum):
    LOCKED = "LOCKED"

    def __str__(self) -> str:
        return str(self.value)
