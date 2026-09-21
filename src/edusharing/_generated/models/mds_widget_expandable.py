from enum import StrEnum


class MdsWidgetExpandable(StrEnum):
    COLLAPSED = "collapsed"
    DISABLED = "disabled"
    EXPANDED = "expanded"

    def __str__(self) -> str:
        return str(self.value)
