from enum import Enum


class CollectionsTypeConfigInvitationType(str, Enum):
    DEFAULT = "Default"
    EDITORIALGROUPS = "EditorialGroups"

    def __str__(self) -> str:
        return str(self.value)
