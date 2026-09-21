from enum import StrEnum


class ShareInfoShareStatus(StrEnum):
    REJECTED = "REJECTED"
    SHARED = "SHARED"

    def __str__(self) -> str:
        return str(self.value)
