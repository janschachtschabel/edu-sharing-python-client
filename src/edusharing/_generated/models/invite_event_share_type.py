from enum import Enum


class InviteEventShareType(str, Enum):
    AUTHORITY = "AUTHORITY"
    LINK = "LINK"

    def __str__(self) -> str:
        return str(self.value)
