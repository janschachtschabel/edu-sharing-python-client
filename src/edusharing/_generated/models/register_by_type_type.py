from enum import Enum


class RegisterByTypeType(str, Enum):
    MOODLE = "moodle"

    def __str__(self) -> str:
        return str(self.value)
