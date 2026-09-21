from enum import StrEnum


class RepositoryMessageUserMode(StrEnum):
    ALL = "all"
    GUEST = "guest"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
