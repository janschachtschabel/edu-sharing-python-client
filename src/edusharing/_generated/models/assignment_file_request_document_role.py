from enum import StrEnum


class AssignmentFileRequestDocumentRole(StrEnum):
    SUBMITTABLE = "SUBMITTABLE"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    def __str__(self) -> str:
        return str(self.value)
