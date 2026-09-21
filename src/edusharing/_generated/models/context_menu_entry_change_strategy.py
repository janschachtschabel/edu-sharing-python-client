from enum import StrEnum


class ContextMenuEntryChangeStrategy(StrEnum):
    REMOVE = "remove"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
