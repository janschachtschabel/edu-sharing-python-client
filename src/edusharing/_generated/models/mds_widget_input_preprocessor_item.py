from enum import Enum


class MdsWidgetInputPreprocessorItem(str, Enum):
    LOWERCASE = "lowercase"
    TRIM = "trim"
    UPPERCASE = "uppercase"

    def __str__(self) -> str:
        return str(self.value)
