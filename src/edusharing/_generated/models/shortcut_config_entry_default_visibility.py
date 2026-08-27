from enum import Enum


class ShortcutConfigEntryDefaultVisibility(str, Enum):
    HIDDEN = "hidden"
    VISIBLE = "visible"

    def __str__(self) -> str:
        return str(self.value)
