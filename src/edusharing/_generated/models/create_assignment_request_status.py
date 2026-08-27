from enum import Enum


class CreateAssignmentRequestStatus(str, Enum):
    CANCELED = "CANCELED"
    CORRECTED = "CORRECTED"
    DRAFT = "DRAFT"
    FINISHED = "FINISHED"
    INPROGRESS = "INPROGRESS"

    def __str__(self) -> str:
        return str(self.value)
