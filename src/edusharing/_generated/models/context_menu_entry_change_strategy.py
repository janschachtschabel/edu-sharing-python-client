from enum import Enum


class ContextMenuEntryChangeStrategy(str, Enum):
    REMOVE = "remove"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
