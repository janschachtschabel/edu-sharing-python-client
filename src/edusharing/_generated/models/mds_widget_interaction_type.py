from enum import StrEnum


class MdsWidgetInteractionType(StrEnum):
    INPUT = "Input"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
