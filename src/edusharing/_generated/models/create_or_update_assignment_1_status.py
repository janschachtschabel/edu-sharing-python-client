from enum import StrEnum


class CreateOrUpdateAssignment1Status(StrEnum):
    CANCELED = "CANCELED"
    CORRECTED = "CORRECTED"
    DRAFT = "DRAFT"
    FINISHED = "FINISHED"
    INPROGRESS = "INPROGRESS"

    def __str__(self) -> str:
        return str(self.value)
