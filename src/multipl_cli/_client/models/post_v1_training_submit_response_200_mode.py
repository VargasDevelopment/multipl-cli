from enum import Enum


class PostV1TrainingSubmitResponse200Mode(str, Enum):
    TRAINING = "training"

    def __str__(self) -> str:
        return str(self.value)
