from enum import Enum


class MdsGroupRendering(str, Enum):
    ANGULAR = "angular"
    LEGACY = "legacy"

    def __str__(self) -> str:
        return str(self.value)
