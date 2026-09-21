from enum import StrEnum


class ConditionType(StrEnum):
    TOOLPERMISSION = "TOOLPERMISSION"

    def __str__(self) -> str:
        return str(self.value)
