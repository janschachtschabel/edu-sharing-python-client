from enum import Enum


class GroupSignupMethod(str, Enum):
    LIST = "list"
    PASSWORD = "password"
    SIMPLE = "simple"

    def __str__(self) -> str:
        return str(self.value)
