from enum import StrEnum


class UserStatusStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    TODELETE = "todelete"

    def __str__(self) -> str:
        return str(self.value)
