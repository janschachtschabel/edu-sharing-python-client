from enum import StrEnum


class CreateAssignmentRequestType(StrEnum):
    DEFAULT = "DEFAULT"
    SUBMISSION = "SUBMISSION"

    def __str__(self) -> str:
        return str(self.value)
