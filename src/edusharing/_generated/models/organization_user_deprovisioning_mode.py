from enum import StrEnum


class OrganizationUserDeprovisioningMode(StrEnum):
    ASSIGN = "assign"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
