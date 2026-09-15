from enum import Enum


class MdsWidgetIsRequired(str, Enum):
    IGNORE = "ignore"
    MANDATORY = "mandatory"
    MANDATORYFORPUBLISH = "mandatoryForPublish"
    OPTIONAL = "optional"
    RECOMMENDED = "recommended"

    def __str__(self) -> str:
        return str(self.value)
