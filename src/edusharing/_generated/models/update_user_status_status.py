from enum import StrEnum


class UpdateUserStatusStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    TODELETE = "todelete"

    def __str__(self) -> str:
        return str(self.value)
