from enum import Enum


class PostV1TrainingLeaseResponse200Mode(str, Enum):
    TRAINING = "training"

    def __str__(self) -> str:
        return str(self.value)
