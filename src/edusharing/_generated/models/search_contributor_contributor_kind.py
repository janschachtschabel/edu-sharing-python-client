from enum import Enum


class SearchContributorContributorKind(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"

    def __str__(self) -> str:
        return str(self.value)
