from enum import Enum


class ShareInfoShareStatus(str, Enum):
    REJECTED = "REJECTED"
    SHARED = "SHARED"

    def __str__(self) -> str:
        return str(self.value)
