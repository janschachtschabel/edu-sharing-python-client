from enum import Enum


class SubmissionValidationStatus(str, Enum):
    FINISHED = "FINISHED"
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
