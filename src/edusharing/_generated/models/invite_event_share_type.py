from enum import StrEnum


class InviteEventShareType(StrEnum):
    AUTHORITY = "AUTHORITY"
    LINK = "LINK"

    def __str__(self) -> str:
        return str(self.value)
