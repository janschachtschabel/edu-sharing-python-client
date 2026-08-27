from enum import Enum


class ToolPermissionEffective(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    UNDEFINED = "UNDEFINED"

    def __str__(self) -> str:
        return str(self.value)
