from enum import Enum


class PermissionRole(str, Enum):
    ASSIGNEE = "ASSIGNEE"
    COORDINATOR = "COORDINATOR"

    def __str__(self) -> str:
        return str(self.value)
