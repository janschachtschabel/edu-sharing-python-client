from enum import StrEnum


class AssignmentType(StrEnum):
    DEFAULT = "DEFAULT"
    SUBMISSION = "SUBMISSION"

    def __str__(self) -> str:
        return str(self.value)
