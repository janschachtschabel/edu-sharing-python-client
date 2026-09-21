from enum import StrEnum


class ShortcutConfigEntryDefaultVisibility(StrEnum):
    HIDDEN = "hidden"
    VISIBLE = "visible"

    def __str__(self) -> str:
        return str(self.value)
