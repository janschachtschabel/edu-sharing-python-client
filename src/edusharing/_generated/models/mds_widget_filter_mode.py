from enum import StrEnum


class MdsWidgetFilterMode(StrEnum):
    ALWAYS = "always"
    AUTO = "auto"
    DISABLED = "disabled"

    def __str__(self) -> str:
        return str(self.value)
