from enum import Enum


class UpdateUserStatusStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    TODELETE = "todelete"

    def __str__(self) -> str:
        return str(self.value)
