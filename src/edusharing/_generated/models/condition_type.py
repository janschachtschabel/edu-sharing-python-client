from enum import Enum


class ConditionType(str, Enum):
    TOOLPERMISSION = "TOOLPERMISSION"

    def __str__(self) -> str:
        return str(self.value)
