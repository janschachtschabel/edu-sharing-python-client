from enum import Enum


class GetCollectionsSubcollectionsScope(str, Enum):
    EDU_ALL = "EDU_ALL"
    EDU_GROUPS = "EDU_GROUPS"
    MY = "MY"
    RECENT = "RECENT"
    TYPE_EDITORIAL = "TYPE_EDITORIAL"
    TYPE_MEDIA_CENTER = "TYPE_MEDIA_CENTER"

    def __str__(self) -> str:
        return str(self.value)
