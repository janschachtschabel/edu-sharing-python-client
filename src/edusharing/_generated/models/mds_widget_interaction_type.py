from enum import Enum


class MdsWidgetInteractionType(str, Enum):
    INPUT = "Input"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
