from enum import Enum


class RepositoryMessageUserMode(str, Enum):
    ALL = "all"
    GUEST = "guest"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
