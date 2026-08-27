from enum import Enum


class RepositoryMessageMode(str, Enum):
    BAR = "bar"
    MODAL = "modal"

    def __str__(self) -> str:
        return str(self.value)
