from enum import Enum


class MdsWidgetExpandable(str, Enum):
    COLLAPSED = "collapsed"
    DISABLED = "disabled"
    EXPANDED = "expanded"

    def __str__(self) -> str:
        return str(self.value)
