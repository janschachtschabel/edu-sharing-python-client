from enum import StrEnum


class OrganizationSignupMethod(StrEnum):
    LIST = "list"
    PASSWORD = "password"
    SIMPLE = "simple"

    def __str__(self) -> str:
        return str(self.value)
