from enum import StrEnum


class UpdateUserStatus1Status(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    TODELETE = "todelete"

    def __str__(self) -> str:
        return str(self.value)
