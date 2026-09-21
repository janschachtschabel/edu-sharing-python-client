from enum import StrEnum


class SearchContributorContributorKind(StrEnum):
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"

    def __str__(self) -> str:
        return str(self.value)
