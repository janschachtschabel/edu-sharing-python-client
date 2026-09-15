from enum import Enum


class PermissionRequestRole(str, Enum):
    ASSIGNEE = "ASSIGNEE"
    COORDINATOR = "COORDINATOR"

    def __str__(self) -> str:
        return str(self.value)
