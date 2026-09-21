from enum import StrEnum


class RegisterByTypeType(StrEnum):
    MOODLE = "moodle"

    def __str__(self) -> str:
        return str(self.value)
