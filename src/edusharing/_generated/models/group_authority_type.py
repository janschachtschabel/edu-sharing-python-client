from enum import StrEnum


class GroupAuthorityType(StrEnum):
    EVERYONE = "EVERYONE"
    GROUP = "GROUP"
    GUEST = "GUEST"
    OWNER = "OWNER"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
