from enum import StrEnum


class ToolPermissionEffective(StrEnum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    UNDEFINED = "UNDEFINED"

    def __str__(self) -> str:
        return str(self.value)
