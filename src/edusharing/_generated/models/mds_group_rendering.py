from enum import StrEnum


class MdsGroupRendering(StrEnum):
    ANGULAR = "angular"
    LEGACY = "legacy"

    def __str__(self) -> str:
        return str(self.value)
