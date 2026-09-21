from enum import StrEnum


class ToolPermissionExplicit(StrEnum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    UNDEFINED = "UNDEFINED"

    def __str__(self) -> str:
        return str(self.value)
