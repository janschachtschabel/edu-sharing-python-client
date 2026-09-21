from enum import StrEnum


class CollectionsTypeConfigInvitationType(StrEnum):
    DEFAULT = "Default"
    EDITORIALGROUPS = "EditorialGroups"

    def __str__(self) -> str:
        return str(self.value)
