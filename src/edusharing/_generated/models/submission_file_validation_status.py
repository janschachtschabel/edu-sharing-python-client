from enum import StrEnum


class SubmissionFileValidationStatus(StrEnum):
    FINISHED = "FINISHED"
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
