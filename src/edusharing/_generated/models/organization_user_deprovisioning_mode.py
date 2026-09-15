from enum import Enum


class OrganizationUserDeprovisioningMode(str, Enum):
    ASSIGN = "assign"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
