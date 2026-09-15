from enum import Enum


class AssignmentFileDocumentRole(str, Enum):
    SUBMITTABLE = "SUBMITTABLE"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    def __str__(self) -> str:
        return str(self.value)
