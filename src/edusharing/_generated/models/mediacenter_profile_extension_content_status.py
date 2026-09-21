from enum import StrEnum


class MediacenterProfileExtensionContentStatus(StrEnum):
    ACTIVATED = "Activated"
    DEACTIVATED = "Deactivated"

    def __str__(self) -> str:
        return str(self.value)
