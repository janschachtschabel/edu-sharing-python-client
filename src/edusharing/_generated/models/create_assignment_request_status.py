from enum import StrEnum


class CreateAssignmentRequestStatus(StrEnum):
    CANCELED = "CANCELED"
    CORRECTED = "CORRECTED"
    DRAFT = "DRAFT"
    FINISHED = "FINISHED"
    INPROGRESS = "INPROGRESS"

    def __str__(self) -> str:
        return str(self.value)
