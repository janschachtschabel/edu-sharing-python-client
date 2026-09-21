from enum import StrEnum


class ListContributorsSortBy(StrEnum):
    CREATED = "CREATED"
    IDS = "IDS"
    KIND = "KIND"
    LAST_UPDATED = "LAST_UPDATED"
    NAME = "NAME"

    def __str__(self) -> str:
        return str(self.value)
