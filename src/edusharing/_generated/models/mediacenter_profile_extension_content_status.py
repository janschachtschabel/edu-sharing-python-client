from enum import Enum


class MediacenterProfileExtensionContentStatus(str, Enum):
    ACTIVATED = "Activated"
    DEACTIVATED = "Deactivated"

    def __str__(self) -> str:
        return str(self.value)
