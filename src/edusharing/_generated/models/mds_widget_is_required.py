from enum import StrEnum


class MdsWidgetIsRequired(StrEnum):
    IGNORE = "ignore"
    MANDATORY = "mandatory"
    MANDATORYFORPUBLISH = "mandatoryForPublish"
    OPTIONAL = "optional"
    RECOMMENDED = "recommended"

    def __str__(self) -> str:
        return str(self.value)
