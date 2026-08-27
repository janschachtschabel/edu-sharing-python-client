from enum import Enum


class StatusMode(str, Enum):
    SEARCH = "SEARCH"
    SERVICE = "SERVICE"

    def __str__(self) -> str:
        return str(self.value)
