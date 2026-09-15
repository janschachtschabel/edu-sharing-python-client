from enum import Enum


class MdsWidgetConditionType(str, Enum):
    PROPERTY = "PROPERTY"
    TOOLPERMISSION = "TOOLPERMISSION"

    def __str__(self) -> str:
        return str(self.value)
