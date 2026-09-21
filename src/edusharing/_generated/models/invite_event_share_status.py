from enum import StrEnum


class InviteEventShareStatus(StrEnum):
    REJECTED = "REJECTED"
    SHARED = "SHARED"

    def __str__(self) -> str:
        return str(self.value)
