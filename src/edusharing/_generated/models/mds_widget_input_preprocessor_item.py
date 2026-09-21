from enum import StrEnum


class MdsWidgetInputPreprocessorItem(StrEnum):
    LOWERCASE = "lowercase"
    TRIM = "trim"
    UPPERCASE = "uppercase"

    def __str__(self) -> str:
        return str(self.value)
