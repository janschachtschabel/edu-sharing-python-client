from enum import StrEnum


class RepositoryMessageMode(StrEnum):
    BAR = "bar"
    MODAL = "modal"

    def __str__(self) -> str:
        return str(self.value)
