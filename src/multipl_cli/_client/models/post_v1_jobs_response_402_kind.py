from enum import Enum


class PostV1JobsResponse402Kind(str, Enum):
    PLATFORM_POST_FEE = "platform_post_fee"

    def __str__(self) -> str:
        return str(self.value)
