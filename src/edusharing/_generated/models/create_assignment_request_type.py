from enum import Enum


class CreateAssignmentRequestType(str, Enum):
    DEFAULT = "DEFAULT"
    SUBMISSION = "SUBMISSION"

    def __str__(self) -> str:
        return str(self.value)
