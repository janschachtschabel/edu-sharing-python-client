from enum import StrEnum


class SubmissionFileValidationRequestValidationStatus(StrEnum):
    FINISHED = "FINISHED"
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
