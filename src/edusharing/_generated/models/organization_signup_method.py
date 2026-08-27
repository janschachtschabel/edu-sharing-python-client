from enum import Enum


class OrganizationSignupMethod(str, Enum):
    LIST = "list"
    PASSWORD = "password"
    SIMPLE = "simple"

    def __str__(self) -> str:
        return str(self.value)
