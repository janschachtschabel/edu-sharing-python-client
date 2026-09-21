from enum import StrEnum


class ListContributorsKind(StrEnum):
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"

    def __str__(self) -> str:
        return str(self.value)
