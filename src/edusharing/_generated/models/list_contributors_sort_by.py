from enum import Enum


class ListContributorsSortBy(str, Enum):
    CREATED = "CREATED"
    IDS = "IDS"
    KIND = "KIND"
    LAST_UPDATED = "LAST_UPDATED"
    NAME = "NAME"

    def __str__(self) -> str:
        return str(self.value)
