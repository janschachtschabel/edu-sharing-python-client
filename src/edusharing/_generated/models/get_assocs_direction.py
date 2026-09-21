from enum import StrEnum


class GetAssocsDirection(StrEnum):
    SOURCE = "SOURCE"
    TARGET = "TARGET"

    def __str__(self) -> str:
        return str(self.value)
