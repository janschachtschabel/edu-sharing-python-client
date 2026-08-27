from enum import Enum


class GetAssocsDirection(str, Enum):
    SOURCE = "SOURCE"
    TARGET = "TARGET"

    def __str__(self) -> str:
        return str(self.value)
