from enum import Enum


class MdsWidgetFilterMode(str, Enum):
    ALWAYS = "always"
    AUTO = "auto"
    DISABLED = "disabled"

    def __str__(self) -> str:
        return str(self.value)
