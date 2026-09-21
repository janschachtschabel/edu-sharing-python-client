from enum import StrEnum


class MdsWidgetConditionType(StrEnum):
    PROPERTY = "PROPERTY"
    TOOLPERMISSION = "TOOLPERMISSION"

    def __str__(self) -> str:
        return str(self.value)
