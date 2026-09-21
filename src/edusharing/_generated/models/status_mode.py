from enum import StrEnum


class StatusMode(StrEnum):
    SEARCH = "SEARCH"
    SERVICE = "SERVICE"

    def __str__(self) -> str:
        return str(self.value)
