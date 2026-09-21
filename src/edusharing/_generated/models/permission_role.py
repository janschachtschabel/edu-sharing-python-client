from enum import StrEnum


class PermissionRole(StrEnum):
    ASSIGNEE = "ASSIGNEE"
    COORDINATOR = "COORDINATOR"

    def __str__(self) -> str:
        return str(self.value)
