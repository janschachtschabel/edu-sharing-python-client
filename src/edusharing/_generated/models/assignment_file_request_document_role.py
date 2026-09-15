from enum import Enum


class AssignmentFileRequestDocumentRole(str, Enum):
    SUBMITTABLE = "SUBMITTABLE"
    SUPPLEMENTARY = "SUPPLEMENTARY"

    def __str__(self) -> str:
        return str(self.value)
