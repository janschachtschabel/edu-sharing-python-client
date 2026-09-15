from enum import Enum


class CreateContributorRequestKind(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"

    def __str__(self) -> str:
        return str(self.value)
