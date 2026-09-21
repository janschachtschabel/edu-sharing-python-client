from enum import StrEnum


class AssignmentFileDocumentRole(StrEnum):
    SUBMITTABLE = "SUBMITTABLE"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    def __str__(self) -> str:
        return str(self.value)
