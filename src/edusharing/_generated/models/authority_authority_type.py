from enum import Enum


class AuthorityAuthorityType(str, Enum):
    EVERYONE = "EVERYONE"
    GROUP = "GROUP"
    GUEST = "GUEST"
    OWNER = "OWNER"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
